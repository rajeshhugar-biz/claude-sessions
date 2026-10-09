"""Offline unit tests (Lab 3). No API key needed.

Run from the code/ folder:  python -m unittest discover -s tests -v
"""
import asyncio
import importlib.util
import random
import sys
import unittest
from pathlib import Path

import httpx

CODE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CODE))


def load(filename: str):
    """Import a demo file whose name starts with a digit (e.g. 02_status_policy.py)."""
    spec = importlib.util.spec_from_file_location(filename[:-3], CODE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


policy = load("02_status_policy.py")
backoff = load("09_backoff.py")
fake = load("11_fake_client.py")
sse = load("12_sse_parser.py")
lab1 = load("lab1_raw_vs_sdk.py")
lab2 = load("lab2_async_pipeline.py")


class StatusPolicy(unittest.TestCase):
    def test_retryable_codes(self):
        for code in (408, 409, 429, 500, 504, 529):
            self.assertEqual(policy.action_for(code), "retry with backoff", code)

    def test_fix_codes(self):
        self.assertEqual(policy.action_for(400), "fix the request")
        self.assertEqual(policy.action_for(404), "fix the request")
        self.assertEqual(policy.action_for(413), "shrink the request")
        self.assertEqual(policy.action_for(401), "fix the key or permissions")


class Backoff(unittest.TestCase):
    def test_ceiling_doubles_then_caps(self):
        top = [backoff.backoff_delay(a, rng=lambda: 1.0) for a in range(8)]
        self.assertEqual(top, [0.5, 1.0, 2.0, 4.0, 8.0, 8.0, 8.0, 8.0])

    def test_jitter_stays_in_range(self):
        for a in range(10):
            d = backoff.backoff_delay(a)
            self.assertTrue(0 <= d <= backoff.CAP)

    def test_with_retries_gives_up(self):
        calls = {"n": 0}

        async def always_fails():
            calls["n"] += 1
            raise backoff.TransientError()

        backoff.BASE = 0.001                    # keep the test fast
        try:
            with self.assertRaises(backoff.TransientError):
                asyncio.run(backoff.with_retries(always_fails, max_attempts=3))
        finally:
            backoff.BASE = 0.5
        self.assertEqual(calls["n"], 3)


class Concurrency(unittest.TestCase):
    def test_semaphore_caps_in_flight(self):
        client = fake.FakeClient(fail_rate=0.3, seed=1)
        out = asyncio.run(fake.run_all(client, [str(i) for i in range(40)], limit=4))
        self.assertEqual(len(out), 40)
        self.assertLessEqual(client.peak, 4)
        self.assertGreater(client.calls, 40)   # some calls were retried


class SSEParser(unittest.TestCase):
    def test_parses_events_and_ignores_comments(self):
        lines = [": keep-alive", "event: ping", 'data: {"type": "ping"}', "",
                 "event: message_stop", 'data: {"type": "message_stop"}', ""]
        events = list(sse.parse_sse(lines))
        self.assertEqual([e for e, _ in events], ["ping", "message_stop"])

    def test_sample_file_text(self):
        raw = (CODE / "sse_sample.txt").read_text().splitlines() + [""]
        text = "".join(p["delta"]["text"] for e, p in sse.parse_sse(raw)
                       if e == "content_block_delta")
        self.assertEqual(
            text, "REST maps resources to URLs and actions to HTTP methods.")


class RawRetries(unittest.TestCase):
    def test_retries_529_then_succeeds(self):
        replies = iter([httpx.Response(529, json={"type": "error"}),
                        httpx.Response(429, headers={"retry-after": "0"}),
                        httpx.Response(200, json={"ok": True})])
        http = httpx.Client(transport=httpx.MockTransport(lambda req: next(replies)))
        waits = []
        resp = lab1.post_with_retries(http, {}, sleep=waits.append)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(waits), 2)
        self.assertEqual(waits[1], 0.0)         # honoured retry-after

    def test_400_is_not_retried(self):
        seen = []

        def handler(req):
            seen.append(req)
            return httpx.Response(400, json={"type": "error"})

        http = httpx.Client(transport=httpx.MockTransport(handler))
        resp = lab1.post_with_retries(http, {}, sleep=lambda s: None)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(len(seen), 1)


class Pipeline(unittest.TestCase):
    def test_lab2_with_fake_client(self):
        random.seed(0)
        client = lab2.FakeAsyncClient(seed=3)
        tickets = [{"id": str(i), "text": f"I was charged twice ({i})"}
                   for i in range(20)]
        results, stats = asyncio.run(lab2.run(client, tickets, limit=5, base=0.001))
        self.assertTrue(all(isinstance(r, lab2.Triage) for r in results))
        self.assertTrue(all(r.category == "billing" for r in results))
        self.assertLessEqual(client.messages.peak, 5)
        self.assertGreater(stats["retries"], 0)

    def test_validator_lowercases_category(self):
        t = lab2.Triage.model_validate_json(
            '{"category": "Billing", "priority": 1, "summary": "double charge"}')
        self.assertEqual(t.category, "billing")


if __name__ == "__main__":
    unittest.main()

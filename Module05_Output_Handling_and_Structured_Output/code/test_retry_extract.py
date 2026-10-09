"""Tests for the retry loop with a fake client (no API key needed).

Run: python -m unittest -v
"""
import inspect
import unittest
from types import SimpleNamespace as NS

import anthropic
from checks import invoice_problems
from invoice_models import Invoice
from retry_extract import ExtractionError, extract_with_retry

GOOD = ('{"invoice_number": "NL-1", "invoice_date": "2026-09-30", '
        '"due_date": null, "vendor_name": "Nimbus", "customer_name": "Acme", '
        '"currency": "INR", "line_items": [{"description": "Seat", '
        '"quantity": 2, "unit_price": 100, "amount": 200}], "subtotal": 200, '
        '"tax_rate_percent": 18, "tax_amount": 36, "total": 236}')


def reply(text, stop="end_turn"):
    return NS(stop_reason=stop, content=[NS(type="text", text=text)])


class FakeClient:
    """Returns scripted responses and records every create() call."""

    def __init__(self, *responses):
        self.responses, self.calls = list(responses), []
        self.messages = self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.responses.pop(0)


class RetryTests(unittest.TestCase):
    def test_success_first_try(self):
        client = FakeClient(reply(GOOD))
        inv, attempts = extract_with_retry(client, Invoice, "x")
        self.assertEqual((inv.total, attempts), (236, 1))
        fmt = client.calls[0]["output_config"]["format"]
        self.assertEqual(fmt["type"], "json_schema")
        self.assertFalse(fmt["schema"]["additionalProperties"])

    def test_thinking_block_is_skipped(self):
        r = NS(stop_reason="end_turn",
               content=[NS(type="thinking", thinking="..."),
                        NS(type="text", text=GOOD)])
        inv, _ = extract_with_retry(FakeClient(r), Invoice, "x")
        self.assertEqual(inv.invoice_number, "NL-1")

    def test_fenced_reply_is_accepted(self):
        client = FakeClient(reply("```json\n" + GOOD + "\n```"))
        self.assertEqual(extract_with_retry(client, Invoice, "x")[1], 1)

    def test_validation_error_is_fed_back(self):
        bad = GOOD.replace('"INR"', '"Rupees"')
        client = FakeClient(reply(bad), reply(GOOD))
        _, attempts = extract_with_retry(client, Invoice, "x")
        self.assertEqual(attempts, 2)
        second = client.calls[1]["messages"]
        self.assertEqual([m["role"] for m in second], ["user", "assistant", "user"])
        self.assertEqual(second[1]["content"], bad)
        self.assertIn("currency", second[2]["content"])

    def test_business_rule_is_fed_back(self):
        wrong_total = GOOD.replace('"total": 236', '"total": 263')
        client = FakeClient(reply(wrong_total), reply(GOOD))
        _, attempts = extract_with_retry(client, Invoice, "x", rules=invoice_problems)
        self.assertEqual(attempts, 2)
        self.assertIn("not 263", client.calls[1]["messages"][2]["content"])

    def test_refusal_stops_immediately(self):
        client = FakeClient(reply("", stop="refusal"), reply(GOOD))
        with self.assertRaises(ExtractionError):
            extract_with_retry(client, Invoice, "x")
        self.assertEqual(len(client.calls), 1)

    def test_max_tokens_doubles_budget(self):
        client = FakeClient(reply(GOOD[:50], stop="max_tokens"), reply(GOOD))
        _, attempts = extract_with_retry(client, Invoice, "x", max_tokens=1000)
        self.assertEqual(attempts, 2)
        self.assertEqual([c["max_tokens"] for c in client.calls], [1000, 2000])

    def test_gives_up_after_max_attempts(self):
        client = FakeClient(*[reply("no json here")] * 3)
        with self.assertRaises(ExtractionError):
            extract_with_retry(client, Invoice, "x", max_attempts=3)
        self.assertEqual(len(client.calls), 3)

    def test_kwargs_match_real_sdk_signature(self):
        client = FakeClient(reply(GOOD))
        extract_with_retry(client, Invoice, "x")
        real = anthropic.Anthropic(api_key="test-key").messages.create
        inspect.signature(real).bind(**client.calls[0])  # TypeError if a name is wrong


if __name__ == "__main__":
    unittest.main()

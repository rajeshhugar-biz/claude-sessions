"""Lab 1 solution: the same request through raw HTTP (httpx) and through the SDK.

Run:  python lab1_raw_vs_sdk.py      (needs ANTHROPIC_API_KEY)
The retry helper is tested offline in tests/test_offline.py with httpx.MockTransport.
"""
import os
import random
import time

import anthropic
import httpx

URL = "https://api.anthropic.com/v1/messages"
BODY = {
    "model": "claude-haiku-4-5-20251001",
    "max_tokens": 200,
    "messages": [{"role": "user", "content": "Give one tip for naming git branches."}],
}
RETRYABLE = {408, 409, 429, 500, 502, 503, 504, 529}


def post_with_retries(http: httpx.Client, body: dict, max_attempts: int = 4,
                      sleep=time.sleep) -> httpx.Response:
    """Everything the SDK does for you on retries, written by hand."""
    for attempt in range(max_attempts):
        last = attempt == max_attempts - 1
        try:
            resp = http.post(URL, json=body)
        except httpx.TransportError:          # network problem: no response at all
            if last:
                raise
            sleep(random.uniform(0, 0.5 * 2 ** attempt))
            continue
        if resp.status_code not in RETRYABLE or last:
            return resp
        wait = resp.headers.get("retry-after")
        sleep(float(wait) if wait else random.uniform(0, 0.5 * 2 ** attempt))
    raise RuntimeError("unreachable")


def raw_call() -> dict:
    headers = {
        "x-api-key": os.environ["ANTHROPIC_API_KEY"],
        "anthropic-version": "2023-06-01",
    }
    t0 = time.perf_counter()
    with httpx.Client(headers=headers, timeout=60.0) as http:
        resp = post_with_retries(http, BODY)
    data = resp.json()
    if resp.is_error:
        raise RuntimeError(f"{resp.status_code} {data['error']['type']}: "
                           f"{data['error']['message']}")
    return {
        "text": "".join(b["text"] for b in data["content"] if b["type"] == "text"),
        "request_id": resp.headers.get("request-id"),
        "tokens": (data["usage"]["input_tokens"], data["usage"]["output_tokens"]),
        "seconds": time.perf_counter() - t0,
    }


def sdk_call() -> dict:
    client = anthropic.Anthropic(timeout=60.0, max_retries=3)
    t0 = time.perf_counter()
    msg = client.messages.create(**BODY)
    return {
        "text": "".join(b.text for b in msg.content if b.type == "text"),
        "request_id": msg._request_id,
        "tokens": (msg.usage.input_tokens, msg.usage.output_tokens),
        "seconds": time.perf_counter() - t0,
    }


if __name__ == "__main__":
    for name, fn in (("raw httpx", raw_call), ("anthropic SDK", sdk_call)):
        r = fn()
        print(f"--- {name}: {r['seconds']:.2f}s, request-id {r['request_id']}, "
              f"tokens in/out {r['tokens']}")
        print(r["text"], "\n")

import anthropic

client = anthropic.Anthropic(
    max_retries=4,            # default is 2 (connection errors, 408, 409, 429, 5xx)
    timeout=120.0,            # seconds; default read timeout is 10 minutes
)

try:
    r = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=512,
        messages=[{"role": "user", "content": "Hello"}],
    )
except anthropic.BadRequestError as e:          # 400: fix the request, don't retry
    print("bad request:", e.message)
except anthropic.AuthenticationError:           # 401: check the API key
    print("check ANTHROPIC_API_KEY")
except anthropic.RateLimitError as e:           # 429: retries exhausted
    print("rate limited; retry-after =", e.response.headers.get("retry-after"))
except anthropic.APIStatusError as e:           # other 4xx/5xx incl. 529 overloaded
    print("API error", e.status_code, "request id:", e.request_id)
except anthropic.APIConnectionError:            # network problem, never reached API
    print("network error")

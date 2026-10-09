"""Build (but do not send) the HTTP request behind a Claude call."""
import json
import os

import httpx

body = {
    "model": "claude-sonnet-5-5",
    "max_tokens": 256,
    "messages": [{"role": "user", "content": "What is an HTTP header?"}],
}
request = httpx.Request(
    "POST",                                    # method
    "https://api.anthropic.com/v1/messages",   # URL: scheme + host + path
    headers={
        "x-api-key": os.environ.get("ANTHROPIC_API_KEY", "sk-ant-demo"),
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    },
    content=json.dumps(body),                  # body: JSON text, sent as bytes
)

print(request.method, request.url)
for name, value in request.headers.items():
    print(f"{name}: {'<redacted>' if name == 'x-api-key' else value}")
print()
print(request.content.decode())

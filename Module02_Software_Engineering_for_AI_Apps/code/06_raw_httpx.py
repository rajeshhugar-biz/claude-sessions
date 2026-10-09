"""Call Claude with plain HTTP (httpx). No SDK."""
import os

import httpx
from dotenv import load_dotenv

load_dotenv()

resp = httpx.post(
    "https://api.anthropic.com/v1/messages",
    headers={
        "x-api-key": os.environ["ANTHROPIC_API_KEY"],
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    },
    json={                                    # httpx serialises the dict for you
        "model": "claude-sonnet-5-5",
        "max_tokens": 256,
        "messages": [{"role": "user", "content": "Explain REST in one sentence."}],
    },
    timeout=60.0,
)

print("status:", resp.status_code, "| request-id:", resp.headers.get("request-id"))
data = resp.json()
if resp.is_error:                             # 4xx / 5xx: body is an error object
    print(data["error"]["type"], "-", data["error"]["message"])
else:
    print("".join(b["text"] for b in data["content"] if b["type"] == "text"))
    print("usage:", data["usage"]["input_tokens"], "in /",
          data["usage"]["output_tokens"], "out")

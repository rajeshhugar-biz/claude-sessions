"""The same call through the official Python SDK."""
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()                # reads ANTHROPIC_API_KEY

try:
    msg = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=256,
        messages=[{"role": "user", "content": "Explain REST in one sentence."}],
    )
except anthropic.APIStatusError as e:         # raised after the built-in retries
    print(e.status_code, type(e).__name__, "| request-id:", e.request_id)
else:
    print("request-id:", msg._request_id)
    print("".join(b.text for b in msg.content if b.type == "text"))
    print("usage:", msg.usage.input_tokens, "in /", msg.usage.output_tokens, "out")

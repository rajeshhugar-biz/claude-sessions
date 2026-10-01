import anthropic
from dotenv import load_dotenv
load_dotenv()  # loads ANTHROPIC_API_KEY from .env
client = anthropic.Anthropic()

r = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=4000,
    thinking={"type": "enabled", "budget_tokens": 2000},
    messages=[{"role": "user", "content":
        "Is 3,599 a prime number? Explain briefly."}],
)
for block in r.content:
    print(block.type, "→", getattr(block, "thinking", None) or block.text)
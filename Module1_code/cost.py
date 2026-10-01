import anthropic
from dotenv import load_dotenv
load_dotenv()
client = anthropic.Anthropic()

PRICES = {  # USD per 1M tokens (input, output)
    "claude-haiku-4-5-20251001": (1, 5),
    "claude-sonnet-5-5": (2, 10),
    "claude-opus-5-5": (4, 20),
}

def cost_usd(model, usage):
    p_in, p_out = PRICES[model]
    return (usage.input_tokens * p_in +
            usage.output_tokens * p_out) / 1_000_000

response = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Explain an LLM in one sentence."}],
)
print(f"${cost_usd(response.model, response.usage):.6f}")

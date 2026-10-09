import anthropic
client = anthropic.Anthropic()

r = client.beta.messages.create(
    model="claude-opus-5-5",
    max_tokens=4096,
    speed="fast",
    betas=["fast-mode-2026-02-01"],
    messages=[{"role": "user", "content": "Refactor this module..."}],
)
print(r.usage.speed)   # "fast" or "standard"
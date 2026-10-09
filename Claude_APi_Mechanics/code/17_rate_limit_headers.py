import anthropic

client = anthropic.Anthropic()

raw = client.messages.with_raw_response.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=20,
    messages=[{"role": "user", "content": "ping"}],
)
for h in ["requests-remaining", "input-tokens-remaining", "output-tokens-remaining"]:
    print(h, "=", raw.headers.get(f"anthropic-ratelimit-{h}"))
print("request-id =", raw.headers.get("request-id"))

message = raw.parse()                         # the normal Message object
print(message.content[0].text)

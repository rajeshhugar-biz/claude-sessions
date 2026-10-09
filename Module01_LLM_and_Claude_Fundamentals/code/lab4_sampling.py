import anthropic
client = anthropic.Anthropic()
prompt = "Suggest a name for a coffee shop. Reply with the name only."

for temp in (0.0, 1.0):
    names = set()
    for _ in range(5):
        r = client.messages.create(
            model="claude-haiku-4-5-20251001", max_tokens=20,
            messages=[{"role": "user", "content": prompt}],
            extra_body={"temperature": temp},
        )
        names.add(r.content[0].text.strip())
    print(f"temperature {temp}: {len(names)} unique -> {names}")

try:
    client.messages.create(
        model="claude-opus-5-5", max_tokens=20,
        messages=[{"role": "user", "content": prompt}],
        extra_body={"temperature": 0.2},
    )
except anthropic.BadRequestError as e:
    print("Opus 5.5 rejected it:", e.message)
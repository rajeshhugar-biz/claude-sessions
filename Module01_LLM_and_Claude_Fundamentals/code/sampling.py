import anthropic
client = anthropic.Anthropic()

prompt = "Suggest a name for a coffee shop. Reply with the name only."

for temp in (0.0, 1.0):
    print(f"--- temperature = {temp}")
    for _ in range(5):
        r = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=20,
            messages=[{"role": "user", "content": prompt}],
            extra_body={"temperature": temp},  # not in SDK 1.x
        )
        print(" ", r.content[0].text)
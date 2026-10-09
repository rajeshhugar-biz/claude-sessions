import anthropic

client = anthropic.Anthropic()
history = []

def chat(user_msg):
    history.append({"role": "user", "content": user_msg})
    r = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=512,
        cache_control={"type": "ephemeral", "ttl": "1h"},   # automatic caching
        system="You are a patient Python tutor.",
        messages=history,
    )
    history.append({"role": "assistant", "content": r.content})
    print("cache read tokens:", r.usage.cache_read_input_tokens)
    return "".join(b.text for b in r.content if b.type == "text")

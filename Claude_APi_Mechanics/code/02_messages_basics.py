import anthropic

client = anthropic.Anthropic()

def text_of(msg):
    return "".join(b.text for b in msg.content if b.type == "text")

response = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=512,
    system="You are a support assistant for Acme Bank. Answer in 2 sentences.",
    messages=[
        {"role": "user", "content": "How do I reset my card PIN?"},
        {"role": "assistant", "content": "You can reset it in the app under Cards > PIN."},
        {"role": "user", "content": "And if I don't have the app?"},
    ],
    stop_sequences=["###"],
)

print(text_of(response))
print("stop_reason:", response.stop_reason)
print("usage:", response.usage.input_tokens, "in /",
      response.usage.output_tokens, "out")
print("request id:", response._request_id)

import anthropic

client = anthropic.Anthropic()

# Large max_tokens: the SDK expects streaming to avoid HTTP timeouts.
with client.messages.stream(
    model="claude-sonnet-5-5",
    max_tokens=64000,
    messages=[{"role": "user",
               "content": "Write a detailed 3,000-word guide to Python packaging."}],
) as stream:
    message = stream.get_final_message()     # streams internally

text = "".join(b.text for b in message.content if b.type == "text")
print(len(text.split()), "words | stop_reason:", message.stop_reason)

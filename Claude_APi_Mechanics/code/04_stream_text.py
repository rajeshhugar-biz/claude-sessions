import anthropic

client = anthropic.Anthropic()

with client.messages.stream(
    model="claude-sonnet-5-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Write a haiku about APIs."}],
) as stream:
    for text in stream.text_stream:          # only the text deltas
        print(text, end="", flush=True)
    final = stream.get_final_message()       # full Message at the end

print("\n\nstop_reason:", final.stop_reason, "| usage:", final.usage)

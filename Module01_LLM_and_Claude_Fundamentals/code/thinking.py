import anthropic
client = anthropic.Anthropic()

r = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=16000,
    thinking={"type": "adaptive", "display": "summarized"},
    output_config={"effort": "high"},
    messages=[{"role": "user", "content":
        "A bat and a ball cost $1.10 in total. The bat costs "
        "$1.00 more than the ball. How much is the ball?"}],
)

for block in r.content:
    if block.type == "thinking":
        print("THINKING:", block.thinking)
    elif block.type == "text":
        print("ANSWER:", block.text)

print(r.usage.output_tokens)
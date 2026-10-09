import anthropic

client = anthropic.Anthropic()

stream = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=256,
    messages=[{"role": "user", "content": "Count to five."}],
    stream=True,                              # raw server-sent events
)

for event in stream:
    if event.type == "message_start":
        print("[start] input tokens:", event.message.usage.input_tokens)
    elif event.type == "content_block_start":
        print(f"[block {event.index} starts: {event.content_block.type}]")
    elif event.type == "content_block_delta":
        if event.delta.type == "text_delta":
            print(event.delta.text, end="", flush=True)
    elif event.type == "content_block_stop":
        print(f"\n[block {event.index} ends]")
    elif event.type == "message_delta":
        print("[delta] stop_reason:", event.delta.stop_reason,
              "| output tokens:", event.usage.output_tokens)
    elif event.type == "message_stop":
        print("[stop]")
    # ping and unknown event types: ignore gracefully

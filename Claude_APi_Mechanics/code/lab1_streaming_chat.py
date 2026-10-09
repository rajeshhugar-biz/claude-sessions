"""Lab 1: a streaming CLI chatbot with memory and a live cost meter."""
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"
PRICE_IN, PRICE_OUT = 2, 10          # USD per 1M tokens (Sonnet 5.5 list price)
SYSTEM = "You are a friendly tutor for beginner Python students. Be concise."

history, total_cost = [], 0.0

while True:
    user = input("\nYou: ").strip()
    if user in {"/quit", "/exit"}:
        break
    if user == "/reset":
        history.clear()
        print("(history cleared)")
        continue
    history.append({"role": "user", "content": user})

    print("Claude: ", end="", flush=True)
    with client.messages.stream(model=MODEL, max_tokens=1024,
                                system=SYSTEM, messages=history) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
        reply = stream.get_final_message()

    history.append({"role": "assistant", "content": reply.content})
    u = reply.usage
    cost = (u.input_tokens * PRICE_IN + u.output_tokens * PRICE_OUT) / 1_000_000
    total_cost += cost
    print(f"\n[{u.input_tokens} in / {u.output_tokens} out | ${cost:.5f} | "
          f"session ${total_cost:.4f}]")
    if reply.stop_reason == "max_tokens":
        print("[warning: answer was cut off at max_tokens]")

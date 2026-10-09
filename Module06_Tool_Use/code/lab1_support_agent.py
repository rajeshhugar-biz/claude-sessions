"""Lab 1 solution: a support agent with weather, calculator and an order DB.

Hand-built agentic loop: call Claude, run every tool it asks for, send all
results back in one user turn, repeat until end_turn. Multi-turn chat with a
token and cost meter. Run setup_db.py first.
"""
import anthropic

from toolbox import MODEL, pick, run_tool, tool_result

SYSTEM = """You are the support assistant for Nimbus Outdoor, an online store in India.
- Use get_order or find_orders for every order fact. Never guess order details.
- Use calculate for every sum, percentage or tax figure.
- When several lookups are independent, call the tools in parallel.
- If a tool returns an error, fix your input or ask the user. Do not invent data.
Amounts are in Indian rupees (INR)."""
TOOLS = pick("get_weather", "calculate", "get_order", "find_orders")
MAX_TURNS = 10                      # per user question
PRICE_IN, PRICE_OUT = 2.00, 10.00   # Sonnet 5.5, USD per million tokens


def answer(client, history, usage):
    """Run the loop on the shared history until Claude ends its turn."""
    for _ in range(MAX_TURNS):
        r = client.messages.create(model=MODEL, max_tokens=2048, system=SYSTEM,
                                   tools=TOOLS, messages=history)
        usage["in"] += r.usage.input_tokens
        usage["out"] += r.usage.output_tokens
        history.append({"role": "assistant", "content": r.content})
        if r.stop_reason != "tool_use":
            if r.stop_reason != "end_turn":
                print(f"   [warning] stop_reason={r.stop_reason}")
            return "".join(b.text for b in r.content if b.type == "text")
        results = []
        for b in r.content:
            if b.type == "tool_use":
                content, is_error = run_tool(b.name, b.input)
                flag = "ERROR " if is_error else ""
                print(f"   [{b.name}] {b.input} -> {flag}{content[:70]}")
                results.append(tool_result(b.id, content, is_error))
        history.append({"role": "user", "content": results})
    return "Sorry, I could not finish that. A colleague will follow up."


def main():
    client = anthropic.Anthropic()
    history, usage = [], {"in": 0, "out": 0}
    print("Nimbus Outdoor support. Type 'quit' to exit.")
    while (question := input("\nYou: ").strip()).lower() not in ("quit", "exit"):
        if not question:
            continue
        history.append({"role": "user", "content": question})
        print("Agent:", answer(client, history, usage))
        cost = (usage["in"] * PRICE_IN + usage["out"] * PRICE_OUT) / 1_000_000
        print(f"   tokens in={usage['in']} out={usage['out']} cost~${cost:.4f}")


if __name__ == "__main__":
    main()

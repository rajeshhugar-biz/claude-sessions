"""A multi-step agent loop: many tools, many turns, until end_turn."""
import anthropic

from toolbox import MODEL, pick, run_tool, tool_result

SYSTEM = ("You are the support assistant for Nimbus Outdoor, an online store. "
          "Use the tools for facts and maths; never guess order details.")
MAX_TURNS = 8                                   # stopping condition #2


def run_agent(client, question, tools, max_turns=MAX_TURNS):
    messages = [{"role": "user", "content": question}]
    for turn in range(1, max_turns + 1):
        r = client.messages.create(model=MODEL, max_tokens=2048, system=SYSTEM,
                                   tools=tools, messages=messages)
        messages.append({"role": "assistant", "content": r.content})  # as-is
        if r.stop_reason == "end_turn":         # stopping condition #1
            return "".join(b.text for b in r.content if b.type == "text")
        if r.stop_reason != "tool_use":         # max_tokens, refusal, ...
            raise RuntimeError(f"stopped early: {r.stop_reason}")
        results = []
        for b in r.content:
            if b.type == "tool_use":
                content, is_error = run_tool(b.name, b.input)
                print(f"  turn {turn}: {b.name}({b.input}) ->",
                      "ERROR" if is_error else "ok", content[:60])
                results.append(tool_result(b.id, content, is_error))
        messages.append({"role": "user", "content": results})  # ONE message
    raise RuntimeError(f"no answer after {max_turns} turns")


if __name__ == "__main__":
    tools = pick("get_order", "calculate", "get_weather")
    print(run_agent(anthropic.Anthropic(),
                    "My order is NB-1002. What did I pay including 18% GST, "
                    "and will I need that rain jacket in Pune today?", tools))

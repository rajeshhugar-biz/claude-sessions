"""Parallel tool calls: run independent calls concurrently, reply in ONE turn."""
from concurrent.futures import ThreadPoolExecutor

import anthropic

from toolbox import MODEL, RISKY, pick, run_tool, tool_result


def run_tool_calls(content):
    calls = [b for b in content if b.type == "tool_use"]
    safe = [b for b in calls if b.name not in RISKY]       # read-only
    with ThreadPoolExecutor(max_workers=4) as pool:
        outputs = dict(zip([b.id for b in safe],
                           pool.map(lambda b: run_tool(b.name, b.input), safe)))
    for b in calls:                                        # side effects:
        if b.id not in outputs:                            # one at a time
            outputs[b.id] = run_tool(b.name, b.input)
    # one tool_result per tool_use, same order, all in ONE user message
    return [tool_result(b.id, *outputs[b.id]) for b in calls]


if __name__ == "__main__":
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content":
                 "Compare today's weather in Pune, Mumbai, Delhi and London."}]
    tools = pick("get_weather")
    while True:
        r = client.messages.create(model=MODEL, max_tokens=1024, tools=tools,
                                   messages=messages)
        messages.append({"role": "assistant", "content": r.content})
        n = sum(b.type == "tool_use" for b in r.content)
        print(f"{r.stop_reason}: {n} tool call(s) in this turn")
        if r.stop_reason != "tool_use":
            break
        messages.append({"role": "user", "content": run_tool_calls(r.content)})
    print("".join(b.text for b in r.content if b.type == "text"))

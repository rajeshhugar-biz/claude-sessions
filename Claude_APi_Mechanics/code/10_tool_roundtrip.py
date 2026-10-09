import anthropic

client = anthropic.Anthropic()

tools = [{
    "name": "get_order_status",
    "description": "Look up the shipping status of an order by its order ID. "
                   "Use when the user asks where their order is.",
    "input_schema": {
        "type": "object",
        "properties": {"order_id": {"type": "string", "description": "e.g. A-10293"}},
        "required": ["order_id"],
    },
}]

def get_order_status(order_id):                  # your real code / database
    return {"order_id": order_id, "status": "shipped", "eta": "2 days"}

messages = [{"role": "user", "content": "Where is my order A-10293?"}]

while True:
    r = client.messages.create(model="claude-sonnet-5-5", max_tokens=1024,
                               tools=tools, messages=messages)
    messages.append({"role": "assistant", "content": r.content})
    if r.stop_reason != "tool_use":
        break
    results = []
    for block in r.content:
        if block.type == "tool_use":
            output = get_order_status(**block.input)
            results.append({"type": "tool_result", "tool_use_id": block.id,
                            "content": str(output)})
    messages.append({"role": "user", "content": results})

print("".join(b.text for b in r.content if b.type == "text"))

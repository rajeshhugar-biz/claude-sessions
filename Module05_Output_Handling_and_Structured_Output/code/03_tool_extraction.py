import anthropic

client = anthropic.Anthropic()
CATEGORIES = ["billing", "bug", "how_to", "other"]

record_ticket = {
    "name": "record_ticket",
    "description": "Save one triaged support ticket. Call it exactly once.",
    "strict": True,  # tool input is guaranteed to match input_schema
    "input_schema": {
        "type": "object",
        "properties": {
            "category": {"type": "string", "enum": CATEGORIES},
            "priority": {"type": "string", "enum": ["low", "medium", "high"]},
            "summary": {"type": "string"},
        },
        "required": ["category", "priority", "summary"],
        "additionalProperties": False,
    },
}

response = client.messages.create(
    model="claude-haiku-4-5-20251001",  # supports forced tool_choice
    max_tokens=1024,
    tools=[record_ticket],
    tool_choice={"type": "tool", "name": "record_ticket"},  # 400 on 5.5 models
    messages=[{"role": "user", "content": "Triage: how do I add a second user?"}],
)
call = next(b for b in response.content if b.type == "tool_use")
print(call.name, call.input)  # input is already a dict: no json.loads needed

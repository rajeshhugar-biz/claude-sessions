import anthropic

client = anthropic.Anthropic()

TOOLS = [
    {"name": "search_tickets", "description": "Full-text search over support "
     "tickets. Returns matching tickets as JSON.",
     "input_schema": {"type": "object", "properties": {"query": {"type": "string"}},
                      "required": ["query"]}},
    {"name": "get_customer_profile", "description": "Customer profile by ID.",
     "input_schema": {"type": "object", "properties": {"id": {"type": "string"}},
                      "required": ["id"]}},
]

CONTEXT_MANAGEMENT = {"edits": [
    {"type": "clear_thinking_20251015",                 # must be listed first
     "keep": {"type": "thinking_turns", "value": 2}},
    {"type": "clear_tool_uses_20250919",
     "trigger": {"type": "input_tokens", "value": 30_000},
     "keep": {"type": "tool_uses", "value": 3},
     "clear_at_least": {"type": "input_tokens", "value": 5_000},
     "exclude_tools": ["get_customer_profile"]},        # never cleared
]}

def step(messages):
    r = client.beta.messages.create(
        model="claude-opus-5-5", max_tokens=4096,
        betas=["context-management-2025-06-27"],
        tools=TOOLS, messages=messages,
        context_management=CONTEXT_MANAGEMENT,
    )
    applied = r.context_management.applied_edits if r.context_management else []
    for edit in applied:
        print(f"[{edit.type}: cleared {edit.cleared_input_tokens:,} tokens]")
    return r            # your full history is unchanged; the API edited its copy

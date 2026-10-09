import json
import anthropic

client = anthropic.Anthropic()

schema = {
    "type": "object",
    "properties": {
        "category": {"type": "string", "enum": ["billing", "bug", "how_to", "other"]},
        "priority": {"type": "string", "enum": ["low", "medium", "high"]},
        "summary": {"type": "string"},
        "order_id": {"type": ["string", "null"]},
    },
    "required": ["category", "priority", "summary", "order_id"],
    "additionalProperties": False,
}

response = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Triage this ticket: I was charged twice "
               "for order A-1042 and need a refund today."}],
    output_config={"format": {"type": "json_schema", "schema": schema}},
)
if response.stop_reason != "end_turn":  # refusal / max_tokens: may not match schema
    raise RuntimeError(f"stopped early: {response.stop_reason}")
text = next(b.text for b in response.content if b.type == "text")
ticket = json.loads(text)
print(ticket["category"], ticket["priority"], ticket["order_id"])

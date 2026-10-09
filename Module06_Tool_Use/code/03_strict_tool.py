"""Strict tool use: tool input always matches the schema (still check meaning)."""
import anthropic

from toolbox import MODEL, get_order, ToolError

LOG_RETURN = {
    "name": "log_return_request",
    "description": (
        "Record a customer's request to return an item. Use it once you know "
        "the order ID and the reason. Does not issue a refund; a person "
        "reviews every return request later."),
    "strict": True,                                   # grammar-constrained input
    "input_schema": {
        "type": "object",
        "properties": {
            "order_id": {"type": "string", "description": "e.g. NB-1001"},
            "reason": {"type": "string",
                       "enum": ["damaged", "wrong_item", "too_small", "other"]},
            "photos_attached": {"type": "boolean"},
        },
        "required": ["order_id", "reason", "photos_attached"],
        "additionalProperties": False,                # always set on strict tools
    },
}

r = anthropic.Anthropic().messages.create(
    model=MODEL, max_tokens=1024, tools=[LOG_RETURN],
    messages=[{"role": "user", "content":
               "My tent from order NB-1005 arrived torn. Photos attached."}])

for block in (b for b in r.content if b.type == "tool_use"):
    print("Schema-valid input:", block.input)         # shape is guaranteed
    try:
        get_order(block.input["order_id"])            # truth is NOT guaranteed
        print("Order exists - safe to record the return.")
    except ToolError as e:
        print("Valid shape, wrong facts:", e)

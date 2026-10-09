"""Errors are results, not crashes: what Claude receives with is_error. Offline."""
import json

from toolbox import run_tool, tool_result

CASES = [  # (what goes wrong, tool name, input Claude sent)
    ("unknown tool", "get_stock", {"sku": "TENT-2"}),
    ("missing argument", "get_order", {}),
    ("bad format", "get_order", {"order_id": "1001"}),
    ("not found", "get_order", {"order_id": "NB-9999"}),
    ("business rule", "issue_refund",            # fails before any write
     {"order_id": "NB-1002", "amount_inr": 3499, "reason": "late"}),
    ("unsafe input", "calculate", {"expression": "__import__('os')"}),
    ("unknown city", "get_weather", {"city": "Atlantis"}),
]

for i, (label, name, tool_input) in enumerate(CASES, 1):
    content, is_error = run_tool(name, tool_input)
    block = tool_result(f"toolu_{i:02}", content, is_error)
    print(f"--- {label}\n{json.dumps(block)}")

# A call you deliberately did NOT run still needs a result:
skipped = tool_result("toolu_99", "Not executed: the previous call failed.", True)
print("--- skipped call\n" + json.dumps(skipped))

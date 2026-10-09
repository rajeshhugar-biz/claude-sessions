"""The SDK tool runner (beta): @beta_tool + tool_runner write the loop for you."""
import json

import anthropic
from anthropic import beta_tool

import toolbox


@beta_tool
def get_order(order_id: str) -> str:
    """Look up one Nimbus Outdoor order by its order ID. Use it when the user
    gives an order ID and asks about status, item or amount. Returns customer,
    item, amount_inr, status and order date.

    Args:
        order_id: Format NB-1234, e.g. NB-1001
    """
    return json.dumps(toolbox.get_order(order_id))   # raise -> is_error result


@beta_tool
def calculate(expression: str) -> str:
    """Evaluate an arithmetic expression exactly. Use it for any maths with
    more than one step. Supports numbers, + - * / ** and brackets only.

    Args:
        expression: e.g. (4999 + 3499) * 0.9
    """
    return json.dumps(toolbox.calculate(expression))   # ToolError -> is_error


client = anthropic.Anthropic()
runner = client.beta.messages.tool_runner(
    model=toolbox.MODEL, max_tokens=2048, max_iterations=8,
    tools=[get_order, calculate],
    messages=[{"role": "user", "content": "What is NB-1005 worth after a "
               "15% discount? Then check NB-7777 too."}])

for message in runner:                          # one item per API response
    for block in message.content:
        if block.type == "tool_use":
            print("tool:", block.name, block.input)
final = runner.until_done()                     # last message, no tool use
print("".join(b.text for b in final.content if b.type == "text"))

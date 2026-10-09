"""Lab 3 solution: port the Lab 1 agent to the SDK tool runner (beta).

Same tools, same system prompt; the runner writes the loop. Compare the
line count and behaviour with lab1_support_agent.py.
"""
import json
import logging

import anthropic
from anthropic import beta_tool

import toolbox
from lab1_support_agent import SYSTEM

logging.basicConfig(level=logging.WARNING)   # runner logs tool tracebacks here


@beta_tool
def get_weather(city: str, unit: str = "celsius") -> str:
    """Get the current weather for one city. Use it when the user asks about
    weather, temperature or rain gear. Returns temp, unit and conditions.

    Args:
        city: City name, e.g. Pune
        unit: celsius or fahrenheit
    """
    return json.dumps(toolbox.get_weather(city, unit))


@beta_tool
def calculate(expression: str) -> str:
    """Evaluate an arithmetic expression exactly. Use it for every sum,
    percentage or tax figure. Numbers, + - * / ** and brackets only.

    Args:
        expression: e.g. (4999 + 3499) * 1.18
    """
    return json.dumps(toolbox.calculate(expression))


@beta_tool
def get_order(order_id: str) -> str:
    """Look up one order by its ID. Use it when the user gives an order ID.
    Returns customer, item, amount_inr, status and order date.

    Args:
        order_id: Format NB-1234
    """
    return json.dumps(toolbox.get_order(order_id))


@beta_tool
def find_orders(email: str, status: str | None = None, limit: int = 5) -> str:
    """List a customer's recent orders by email, newest first. Use it when the
    user does not know the order ID. Returns order_id, item, amount, status.

    Args:
        email: Customer email address
        status: Optional filter, e.g. delivered
        limit: Maximum orders to return, 1-20
    """
    return json.dumps(toolbox.find_orders(email, status, limit))


def ask(client, question):
    runner = client.beta.messages.tool_runner(
        model=toolbox.MODEL, max_tokens=2048, max_iterations=10, system=SYSTEM,
        tools=[get_weather, calculate, get_order, find_orders],
        messages=[{"role": "user", "content": question}])
    for message in runner:
        response = runner.generate_tool_call_response()   # peek at results
        for block in (response or {}).get("content", []):
            flag = "ERROR " if block.get("is_error") else ""
            print(f"   [tool result] {flag}{str(block.get('content'))[:70]}")
    final = runner.until_done()
    return "".join(b.text for b in final.content if b.type == "text")


if __name__ == "__main__":
    client = anthropic.Anthropic()
    print(ask(client, "I'm asha@example.com. List my orders, total what I've "
                      "spent, and tell me if I need the jacket in Mumbai today."))

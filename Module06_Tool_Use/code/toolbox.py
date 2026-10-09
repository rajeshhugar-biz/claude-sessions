"""Shared tools for the Module 6 demos: weather, calculator, orders DB, refunds.

Every demo imports from here, so the tool code is written once and tested once
(see test_toolbox.py). Data is fictional. Run setup_db.py first.
"""
import ast
import json
import operator
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from anthropic.lib.tools import ToolError as SDKToolError

MODEL = "claude-sonnet-5-5"
DB_PATH = Path(__file__).with_name("shop.db")


class ToolError(SDKToolError):
    """A failure Claude should see and can act on. Sent back with is_error.

    Subclasses the SDK's ToolError, so the tool runner (11_tool_runner.py)
    also sends just this message, without logging a traceback.
    """


# ---------------------------------------------------------------- weather
_WEATHER = {  # fake data: the demos need no weather API key
    "pune": (31, "sunny"), "mumbai": (29, "humid, light rain"),
    "delhi": (34, "hazy"), "london": (14, "overcast"),
}


def get_weather(city, unit="celsius"):
    temp_c, conditions = _WEATHER.get(city.strip().lower(), (None, None))
    if temp_c is None:
        known = ", ".join(c.title() for c in _WEATHER)
        raise ToolError(f"No weather data for '{city}'. Known cities: {known}.")
    temp = temp_c if unit == "celsius" else round(temp_c * 9 / 5 + 32)
    return {"city": city.title(), "temp": temp, "unit": unit,
            "conditions": conditions}


# ------------------------------------------------------------- calculator
_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
        ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg}


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 100:
            raise ToolError("Exponent too large (max 100).")
        return _OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ToolError("Only numbers and + - * / ** ( ) are allowed.")


def calculate(expression):
    """Safe arithmetic. Never use eval() on model output."""
    try:
        value = _eval(ast.parse(expression, mode="eval").body)
    except SyntaxError:
        raise ToolError(f"Could not parse '{expression}'. Example: (4999 * 0.18)")
    except ZeroDivisionError:
        raise ToolError("Division by zero.")
    return {"expression": expression, "result": round(value, 4)}


# ------------------------------------------------------------- orders DB
ORDER_ID = re.compile(r"^NB-\d{4}$")


@contextmanager
def _db():
    if not Path(DB_PATH).exists():
        raise RuntimeError("shop.db missing - run setup_db.py")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        with conn:                               # commit on success
            yield conn
    finally:
        conn.close()


def get_order(order_id):
    if not ORDER_ID.match(order_id):
        raise ToolError(f"'{order_id}' is not a valid order ID. Format: NB-1234.")
    with _db() as conn:
        row = conn.execute(
            "SELECT o.order_id, c.name AS customer, o.item, o.amount_inr,"
            " o.status, o.ordered_on FROM orders o JOIN customers c"
            " USING (customer_id) WHERE o.order_id = ?", (order_id,)).fetchone()
    if row is None:
        raise ToolError(f"No order {order_id}. Ask the customer to check the ID.")
    return dict(row)


def find_orders(email, status=None, limit=5):
    sql = ("SELECT o.order_id, o.item, o.amount_inr, o.status FROM orders o"
           " JOIN customers c USING (customer_id) WHERE c.email = ?")
    args = [email.strip().lower()]
    if status:
        sql += " AND o.status = ?"
        args.append(status)
    with _db() as conn:
        rows = conn.execute(sql + " ORDER BY o.ordered_on DESC LIMIT ?",
                            (*args, min(int(limit), 20))).fetchall()
    if not rows:
        raise ToolError(f"No orders found for {email}"
                        + (f" with status '{status}'." if status else "."))
    return {"email": email, "orders": [dict(r) for r in rows]}


def issue_refund(order_id, amount_inr, reason):
    """RISKY: moves money. Only ever called after human approval."""
    order = get_order(order_id)
    if order["status"] != "delivered":
        raise ToolError(f"Order {order_id} is '{order['status']}'. "
                        "Only delivered orders can be refunded.")
    if not 0 < amount_inr <= order["amount_inr"]:
        raise ToolError(f"Amount must be between 1 and {order['amount_inr']}.")
    with _db() as conn:
        cur = conn.execute(
            "INSERT INTO refunds (order_id, amount_inr, reason, created_at)"
            " VALUES (?, ?, ?, ?)",
            (order_id, amount_inr, reason, datetime.now().isoformat()))
        conn.execute("UPDATE orders SET status = 'refunded' WHERE order_id = ?",
                     (order_id,))
    return {"refund_id": cur.lastrowid, "order_id": order_id,
            "amount_inr": amount_inr, "status": "refunded"}


# ----------------------------------------------------- tool definitions
TOOL_DEFS = {
    "get_weather": {
        "name": "get_weather",
        "description": (
            "Get the current weather for one city. Use it when the user asks "
            "about weather, temperature or whether to carry rain gear. Returns "
            "temp, unit and a short conditions text. Covers only a few demo "
            "cities; if a city is unknown the error lists the cities it knows."),
        "input_schema": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "City name, e.g. Pune"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"],
                         "description": "Default celsius"},
            },
            "required": ["city"],
        },
    },
    "calculate": {
        "name": "calculate",
        "description": (
            "Evaluate an arithmetic expression exactly. Use it for any maths "
            "with more than one step: totals, percentages, GST, differences. "
            "Supports numbers, + - * / ** and brackets only, no functions or "
            "variables. Returns the expression and the numeric result."),
        "input_schema": {
            "type": "object",
            "properties": {"expression": {
                "type": "string", "description": "e.g. (4999 + 3499) * 0.9"}},
            "required": ["expression"],
        },
    },
    "get_order": {
        "name": "get_order",
        "description": (
            "Look up one Nimbus Outdoor order by its order ID. Use it when the "
            "user gives an order ID and asks about status, item or amount. "
            "Returns customer name, item, amount_inr, status and order date. "
            "Use find_orders instead when the user only gives an email."),
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {
                "type": "string", "description": "Format NB-1234, e.g. NB-1001"}},
            "required": ["order_id"],
        },
    },
    "find_orders": {
        "name": "find_orders",
        "description": (
            "List a customer's recent orders by their email address, newest "
            "first. Use it when the user does not know the order ID. Returns "
            "order_id, item, amount_inr and status for at most `limit` orders. "
            "Optionally filter by status."),
        "input_schema": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "description": "Customer email"},
                "status": {"type": "string", "enum": [
                    "processing", "shipped", "delivered", "cancelled",
                    "refunded"]},
                "limit": {"type": "integer", "description": "1-20, default 5"},
            },
            "required": ["email"],
        },
    },
    "issue_refund": {
        "name": "issue_refund",
        "description": (
            "Refund a delivered order, fully or partly. This moves real money "
            "and cannot be undone. Use it only after you have looked up the "
            "order and the user has clearly asked for a refund. A human "
            "reviews every call before it runs; if they decline, do not retry."),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "e.g. NB-1001"},
                "amount_inr": {"type": "integer",
                               "description": "Whole rupees, at most the order"},
                "reason": {"type": "string", "description": "Short reason"},
            },
            "required": ["order_id", "amount_inr", "reason"],
        },
    },
}

REGISTRY = {"get_weather": get_weather, "calculate": calculate,
            "get_order": get_order, "find_orders": find_orders,
            "issue_refund": issue_refund}
RISKY = {"issue_refund"}            # side effects: need human approval
TOOLS = list(TOOL_DEFS.values())


def pick(*names):
    """Choose a subset of tools for a demo, e.g. pick('calculate')."""
    return [TOOL_DEFS[n] for n in names]


# ----------------------------------------------------------- dispatcher
def run_tool(name, tool_input):
    """Run one tool call. Returns (content, is_error). Never raises."""
    fn = REGISTRY.get(name)
    if fn is None:
        return f"Unknown tool '{name}'. Available: {', '.join(REGISTRY)}.", True
    try:
        result = fn(**tool_input)
    except ToolError as e:                       # expected, actionable
        return str(e), True
    except TypeError as e:                       # wrong or missing arguments
        return f"Bad arguments for {name}: {e}", True
    except Exception as e:                       # unexpected: hide internals
        return (f"{name} failed ({type(e).__name__}). "
                "Tell the user to try again later."), True
    return json.dumps(result), False


def tool_result(tool_use_id, content, is_error=False):
    block = {"type": "tool_result", "tool_use_id": tool_use_id,
             "content": content}
    if is_error:
        block["is_error"] = True
    return block

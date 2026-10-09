"""Offline unit tests: tool functions, dispatcher, gates and the agent loop.

Run:  python -m unittest -v test_toolbox.py      (no API key needed)
Each test uses a fresh temporary copy of the order database.
"""
import importlib
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from anthropic.types import Message

import setup_db
import toolbox
from toolbox import ToolError, run_tool, tool_result

design = importlib.import_module("01_tool_design")
choice = importlib.import_module("02_tool_choice")
loop = importlib.import_module("04_agent_loop")
parallel = importlib.import_module("05_parallel_calls")
gate = importlib.import_module("07_approval_gate")
editor = importlib.import_module("10_text_editor_tool")
lab2 = importlib.import_module("lab2_refund_guardrails")
lab3 = importlib.import_module("lab3_tool_runner_port")


def reply(stop_reason, *blocks):
    """A real SDK Message object, as the API would return it."""
    return Message.model_validate({
        "id": "msg_test", "type": "message", "role": "assistant",
        "model": "test", "content": list(blocks), "stop_reason": stop_reason,
        "stop_sequence": None, "usage": {"input_tokens": 1, "output_tokens": 1}})


def use(block_id, name, tool_input):
    return {"type": "tool_use", "id": block_id, "name": name, "input": tool_input}


def text(t):
    return {"type": "text", "text": t}


class FakeClient:
    """Stands in for anthropic.Anthropic(): returns scripted replies in order."""

    def __init__(self, *replies):
        self.replies, self.calls = list(replies), []
        self.messages = self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return self.replies.pop(0)


class DBTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        db = setup_db.create(Path(self.tmp.name) / "shop.db")
        patcher = mock.patch.object(toolbox, "DB_PATH", db)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(self.tmp.cleanup)
        self.db = db

    def status(self, order_id):
        with sqlite3.connect(self.db) as conn:
            return conn.execute("SELECT status FROM orders WHERE order_id = ?",
                                (order_id,)).fetchone()[0]


class TestWeatherAndCalculator(unittest.TestCase):
    def test_weather_units(self):
        self.assertEqual(toolbox.get_weather("pune")["temp"], 31)
        self.assertEqual(toolbox.get_weather("Pune", "fahrenheit")["temp"], 88)

    def test_unknown_city_lists_known_cities(self):
        with self.assertRaisesRegex(ToolError, "Known cities: Pune"):
            toolbox.get_weather("Atlantis")

    def test_arithmetic(self):
        self.assertEqual(toolbox.calculate("(4999 + 3499) * 0.9")["result"], 7648.2)
        self.assertEqual(toolbox.calculate("-2 ** 2")["result"], -4)
        self.assertEqual(toolbox.calculate("10 / 4")["result"], 2.5)

    def test_calculator_rejects_code_and_bad_input(self):
        for expr in ["__import__('os')", "abs(-1)", "x + 1", "2 ** 1000", "1/0",
                     "2 +"]:
            with self.subTest(expr=expr), self.assertRaises(ToolError):
                toolbox.calculate(expr)


class TestOrders(DBTestCase):
    def test_get_order_returns_only_needed_fields(self):
        order = toolbox.get_order("NB-1001")
        self.assertEqual(order["customer"], "Asha Verma")
        self.assertEqual(set(order), {"order_id", "customer", "item", "amount_inr",
                                      "status", "ordered_on"})

    def test_get_order_errors_are_actionable(self):
        with self.assertRaisesRegex(ToolError, "Format: NB-1234"):
            toolbox.get_order("1001")
        with self.assertRaisesRegex(ToolError, "check the ID"):
            toolbox.get_order("NB-9999")

    def test_find_orders(self):
        result = toolbox.find_orders("ROHAN@example.com ")
        self.assertEqual([o["order_id"] for o in result["orders"]],
                         ["NB-1004", "NB-1003"])               # newest first
        delivered = toolbox.find_orders("rohan@example.com", "delivered")
        self.assertEqual(len(delivered["orders"]), 1)
        with self.assertRaises(ToolError):
            toolbox.find_orders("nobody@example.com")

    def test_refund_happy_path(self):
        out = toolbox.issue_refund("NB-1003", 2799, "stopped working")
        self.assertEqual(out["status"], "refunded")
        self.assertEqual(self.status("NB-1003"), "refunded")

    def test_refund_business_rules(self):
        with self.assertRaisesRegex(ToolError, "Only delivered"):
            toolbox.issue_refund("NB-1002", 100, "late")         # shipped
        with self.assertRaisesRegex(ToolError, "between 1 and 4999"):
            toolbox.issue_refund("NB-1001", 5000, "too much")
        toolbox.issue_refund("NB-1001", 100, "strap broke")
        with self.assertRaises(ToolError):                      # no double refund
            toolbox.issue_refund("NB-1001", 100, "strap broke")


class TestDispatcher(DBTestCase):
    def test_success_is_json(self):
        content, is_error = run_tool("get_order", {"order_id": "NB-1005"})
        self.assertFalse(is_error)
        self.assertEqual(json.loads(content)["item"], "Two-person tent")

    def test_errors_never_raise(self):
        cases = [("no_such_tool", {}), ("get_order", {}),
                 ("get_order", {"order_id": "NB-1", "extra": 1}),
                 ("issue_refund", {"order_id": "NB-1001", "amount_inr": "all",
                                   "reason": "x"})]
        for name, args in cases:
            with self.subTest(name=name, args=args):
                content, is_error = run_tool(name, args)
                self.assertTrue(is_error)
                self.assertIsInstance(content, str)

    def test_unexpected_failure_hides_internals(self):
        with mock.patch.object(toolbox, "DB_PATH", Path("/nonexistent/x.db")):
            content, is_error = run_tool("get_order", {"order_id": "NB-1001"})
        self.assertTrue(is_error)
        self.assertIn("try again later", content)
        self.assertNotIn("/nonexistent", content)

    def test_tool_result_shape(self):
        self.assertNotIn("is_error", tool_result("t1", "ok"))
        self.assertTrue(tool_result("t1", "bad", True)["is_error"])


class TestDefinitions(unittest.TestCase):
    def test_every_tool_is_defined_and_registered(self):
        self.assertEqual(set(toolbox.TOOL_DEFS), set(toolbox.REGISTRY))
        for name, tool in toolbox.TOOL_DEFS.items():
            self.assertEqual(tool["name"], name)

    def test_linter(self):
        for tool in toolbox.TOOLS:
            self.assertEqual(design.lint_tool(tool), [], tool["name"])
        self.assertGreaterEqual(len(design.lint_tool(design.WEAK)), 4)
        strict_bad = {**toolbox.TOOL_DEFS["calculate"], "strict": True}
        self.assertIn("strict tool: set additionalProperties to false",
                      design.lint_tool(strict_bad))

    def test_beta_tool_schemas_match_hand_written_ones(self):
        schema = lab3.find_orders.to_dict()["input_schema"]
        self.assertEqual(schema["required"], ["email"])
        self.assertEqual(lab3.get_order.to_dict()["name"], "get_order")

    def test_tool_choice_guard(self):
        with self.assertRaises(ValueError):
            choice.checked_choice("claude-opus-5-5", {"type": "any"})
        with self.assertRaises(ValueError):
            choice.checked_choice("claude-sonnet-5-5",
                                  {"type": "tool", "name": "calculate"})
        forced = {"type": "tool", "name": "calculate"}
        self.assertIs(choice.checked_choice("claude-haiku-4-5-20251001", forced),
                      forced)
        self.assertEqual(choice.checked_choice("claude-opus-5-5", {"type": "none"}),
                         {"type": "none"})


class TestAgentLoop(DBTestCase):
    def test_parallel_calls_answered_in_one_user_turn(self):
        client = FakeClient(
            reply("tool_use", text("Checking."),
                  use("t1", "get_order", {"order_id": "NB-1002"}),
                  use("t2", "get_order", {"order_id": "NB-7777"})),
            reply("tool_use", use("t3", "calculate", {"expression": "3499*1.18"})),
            reply("end_turn", text("You paid 4128.82 including GST.")))
        with mock.patch("builtins.print"):
            answer = loop.run_agent(client, "q", toolbox.TOOLS)
        self.assertEqual(answer, "You paid 4128.82 including GST.")
        history = client.calls[-1]["messages"]
        roles = [m["role"] for m in history]
        self.assertEqual(roles, ["user", "assistant", "user", "assistant", "user",
                                 "assistant"])
        results = history[2]["content"]
        self.assertEqual([r["tool_use_id"] for r in results], ["t1", "t2"])
        self.assertNotIn("is_error", results[0])
        self.assertTrue(results[1]["is_error"])
        self.assertEqual(history[1]["content"][0].type, "text")   # sent back as-is

    def test_loop_stops(self):
        endless = [reply("tool_use", use(f"t{i}", "calculate",
                                         {"expression": "1+1"})) for i in range(3)]
        with mock.patch("builtins.print"), \
                self.assertRaisesRegex(RuntimeError, "after 3 turns"):
            loop.run_agent(FakeClient(*endless), "q", toolbox.TOOLS, max_turns=3)
        with self.assertRaisesRegex(RuntimeError, "max_tokens"):
            loop.run_agent(FakeClient(reply("max_tokens", text("cut"))), "q", [])

    def test_parallel_runner_keeps_order_and_runs_risky_last(self):
        msg = reply("tool_use",
                    use("a", "issue_refund", {"order_id": "NB-1003",
                                              "amount_inr": 10, "reason": "test"}),
                    use("b", "get_weather", {"city": "Pune"}),
                    use("c", "get_order", {"order_id": "NB-1003"}))
        results = parallel.run_tool_calls(msg.content)
        self.assertEqual([r["tool_use_id"] for r in results], ["a", "b", "c"])
        self.assertEqual(json.loads(results[2]["content"])["status"], "delivered")


class TestApprovalGates(DBTestCase):
    REFUND = use("r1", "issue_refund", {"order_id": "NB-1003", "amount_inr": 2799,
                                        "reason": "stopped working"})

    def block(self):
        return reply("tool_use", self.REFUND).content[0]

    def test_declined_refund_changes_nothing(self):
        result = gate.gated_call(self.block(), lambda n, a: (False, "need photo"))
        self.assertTrue(result["is_error"])
        self.assertIn("need photo", result["content"])
        self.assertEqual(self.status("NB-1003"), "delivered")

    def test_approved_refund_runs(self):
        result = gate.gated_call(self.block(), lambda n, a: (True, "y"))
        self.assertNotIn("is_error", result)
        self.assertEqual(self.status("NB-1003"), "refunded")

    def test_safe_tools_skip_the_approver(self):
        block = reply("tool_use", use("w", "get_weather", {"city": "Pune"})).content[0]

        def approver(name, args):
            raise AssertionError("approver must not be called")
        self.assertNotIn("is_error", gate.gated_call(block, approver))

    def test_lab2_policy_refuses_before_asking_a_human(self):
        log = Path(self.tmp.name) / "audit.jsonl"
        big = reply("tool_use", use("r2", "issue_refund", {
            "order_id": "NB-1005", "amount_inr": 12999,
            "reason": "tent leaks"})).content[0]

        def approver(name, args):
            raise AssertionError("policy should refuse first")
        with mock.patch.object(lab2, "AUDIT_LOG", log):
            result = lab2.handle(big, approver)
            ok = lab2.handle(self.block(), lambda n, a: (True, "y"))
        self.assertTrue(result["is_error"])
        self.assertIn("desk limit", result["content"])
        self.assertNotIn("is_error", ok)
        events = [json.loads(line) for line in log.read_text().splitlines()]
        self.assertEqual([e.get("approved") for e in events], [False, True, None])


class TestTextEditorHandler(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name).resolve()
        patcher = mock.patch.object(editor, "ROOT", root)
        patcher.start()
        self.addCleanup(patcher.stop)
        (root / "notes.md").write_text("a\nb b\n")

    def run_cmd(self, **cmd):
        return editor.handle_editor(cmd)

    def test_view_numbers_lines(self):
        self.assertEqual(self.run_cmd(command="view", path="/notes.md"),
                         ("1: a\n2: b b", False))

    def test_str_replace_needs_exactly_one_match(self):
        self.assertTrue(self.run_cmd(command="str_replace", path="/notes.md",
                                     old_str="b", new_str="c")[1])
        content, err = self.run_cmd(command="str_replace", path="/notes.md",
                                    old_str="a", new_str="z")
        self.assertFalse(err)
        self.assertIn("exactly one location", content)

    def test_insert_and_create(self):
        self.run_cmd(command="insert", path="/notes.md", insert_line=0,
                     insert_text="# Title")
        self.assertEqual(self.run_cmd(command="view", path="/notes.md")[0][:10],
                         "1: # Title")
        self.assertFalse(self.run_cmd(command="create", path="/new.md",
                                      file_text="hi")[1])

    def test_path_traversal_blocked(self):
        content, err = self.run_cmd(command="view", path="/../../etc/passwd")
        self.assertTrue(err)
        self.assertIn("outside the workspace", content)


if __name__ == "__main__":
    unittest.main()

"""Lab 2 solution: refunds behind a policy check, human approval and an audit log.

Layers, in order: (1) deterministic policy rules in code, (2) a human approver,
(3) the tool's own validation in toolbox.issue_refund, (4) an audit trail.
Run setup_db.py first (it also resets any refunds made in an earlier run).
"""
import json
from datetime import datetime
from pathlib import Path

import anthropic

from toolbox import MODEL, RISKY, pick, run_tool, tool_result

AUDIT_LOG = Path(__file__).with_name("refund_audit.jsonl")
DESK_LIMIT_INR = 10000


def policy_check(name, args):
    """Rules that never need a human. Returns a reason to refuse, or None."""
    if name == "issue_refund":
        if args.get("amount_inr", 0) > DESK_LIMIT_INR:
            return f"over the INR {DESK_LIMIT_INR} desk limit; needs a manager"
        if len(args.get("reason", "")) < 5:
            return "a refund needs a real reason"
    return None


def audit(**event):
    event["at"] = datetime.now().isoformat(timespec="seconds")
    with AUDIT_LOG.open("a") as f:
        f.write(json.dumps(event) + "\n")


def console_approver(name, args):
    print(f"\n  APPROVAL NEEDED: {name} {args}")
    reply = input("  Approve? [y/N] or type a reason to decline: ").strip()
    return reply.lower() == "y", reply


def handle(block, approver=console_approver):
    """Build the tool_result for one tool_use block, applying every layer."""
    if block.name in RISKY:
        refusal = policy_check(block.name, block.input)
        approved, note = (False, "policy: " + refusal) if refusal else \
            approver(block.name, block.input)
        audit(tool=block.name, input=block.input, approved=approved, note=note)
        if not approved:
            return tool_result(block.id, f"Not done ({note}). Nothing changed. "
                               "Do not retry; offer to escalate.", is_error=True)
    content, is_error = run_tool(block.name, block.input)
    if block.name in RISKY:
        audit(tool=block.name, result=content, is_error=is_error)
    return tool_result(block.id, content, is_error)


def run(client, question, approver=console_approver, max_turns=8):
    messages = [{"role": "user", "content": question}]
    tools = pick("get_order", "find_orders", "calculate", "issue_refund")
    for _ in range(max_turns):
        r = client.messages.create(model=MODEL, max_tokens=2048, tools=tools,
                                   messages=messages)
        messages.append({"role": "assistant", "content": r.content})
        if r.stop_reason != "tool_use":
            return "".join(b.text for b in r.content if b.type == "text")
        messages.append({"role": "user", "content": [
            handle(b, approver) for b in r.content if b.type == "tool_use"]})
    return "Stopped: too many turns."


if __name__ == "__main__":
    client = anthropic.Anthropic()
    for q in ["Please refund my tent, order NB-1005, in full. It leaks.",
              "Refund INR 1000 on NB-1001, one strap broke on day two."]:
        print("\nUSER:", q, "\nAGENT:", run(client, q))
    print(f"\nAudit trail written to {AUDIT_LOG.name}")

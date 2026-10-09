"""Human-in-the-loop: a person approves every risky tool call before it runs."""
import anthropic

from toolbox import MODEL, RISKY, pick, run_tool, tool_result


def ask_human(name, tool_input):
    """Approver: returns (approved, note). Swap for Slack, a ticket, a UI..."""
    print(f"\n  APPROVAL NEEDED: {name} {tool_input}")
    answer = input("  Approve? [y/N] or type a reason to decline: ").strip()
    return answer.lower() == "y", answer


def gated_call(block, approver=ask_human):
    if block.name in RISKY:
        approved, note = approver(block.name, block.input)
        if not approved:                      # tell Claude clearly, as an error
            return tool_result(block.id, "Declined by a human reviewer "
                               f"(note: {note or 'none'}). Nothing was changed. "
                               "Do not retry; tell the user it was escalated.",
                               is_error=True)
    return tool_result(block.id, *run_tool(block.name, block.input))


if __name__ == "__main__":
    client = anthropic.Anthropic()
    tools = pick("get_order", "issue_refund")
    messages = [{"role": "user", "content": "My stove from NB-1003 stopped "
                 "working after a week. Please refund me in full."}]
    for _ in range(6):                        # max turns
        r = client.messages.create(model=MODEL, max_tokens=1024, tools=tools,
                                   messages=messages)
        messages.append({"role": "assistant", "content": r.content})
        if r.stop_reason != "tool_use":
            break
        results = [gated_call(b) for b in r.content if b.type == "tool_use"]
        messages.append({"role": "user", "content": results})
    print("".join(b.text for b in r.content if b.type == "text"))

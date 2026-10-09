"""Lab 1: a 50-turn chat that degrades, then fixed with pruning + summarisation.

Offline by default (token estimates and fact checks). Add --live to ask Claude a
recall question against each final context (needs ANTHROPIC_API_KEY).
"""
import importlib
import json
import sys
from pathlib import Path

sim = importlib.import_module("01_long_chat_simulator")
pruner = importlib.import_module("02_tool_output_pruner")
clearer = importlib.import_module("03_clear_old_results")
memory = importlib.import_module("08_window_memory")

BUDGET = 12_000                       # pretend context budget (estimated tokens)
SYSTEM = "You are Acme's support agent. Be brief and accurate."
FACTS = {1: "Hi, my name is Ravi.", 2: "My other order is ORD-51177.",
         4: "I live in Nashik.", 6: "The deadline is Friday evening."}
CHECKS = ["my name is Ravi", "ORD-51177", "Nashik", "Friday evening"]
RAW_ORDER = json.loads(Path("data/order_api_response.json").read_text())
KEEP = {"order", "id", "status", "shipping", "eta", "items", "name", "qty"}

def turn_events(t):
    """What happens in turn t: (user text, tool payload or None, reply)."""
    user = FACTS.get(t, f"Turn {t}: another question about my delivery " * 3)
    tool = RAW_ORDER if t % 3 == 0 else None
    return user, tool, f"Reply {t}: " + "here is some helpful detail " * 8

def tool_pair(t, payload, prune_it):
    call = {"type": "tool_use", "id": f"toolu_{t}", "name": "get_order",
            "input": {"order_id": "ORD-48213"}}
    if prune_it:
        result = pruner.to_tool_result(f"toolu_{t}", payload, fields=KEEP,
                                       max_items=3)
    else:
        result = {"type": "tool_result", "tool_use_id": f"toolu_{t}",
                  "content": json.dumps(payload, indent=2)}
    return [{"role": "assistant", "content": [call]},
            {"role": "user", "content": [result]}]

def size(system, msgs):
    return sim.est_tokens(system) + sim.est_tokens(msgs)

def truncate(msgs, system):
    """Drop the oldest turns until under budget (start on a plain user turn)."""
    while size(system, msgs) > BUDGET and len(msgs) > 2:
        msgs = msgs[1:]
        while msgs and not memory.plain_user(msgs[0]):
            msgs = msgs[1:]
    return msgs

def run(strategy, turns=50):
    msgs, mem, sizes = [], memory.WindowMemory(memory.fact_keeper, window=12), []
    for t in range(1, turns + 1):
        user, tool, reply = turn_events(t)
        new = [{"role": "user", "content": user}]
        if tool:
            new += tool_pair(t, tool, prune_it=(strategy == "managed"))
        new.append({"role": "assistant", "content": reply})
        if strategy == "managed":
            for m in new:
                mem.add(m["role"], m["content"])
            mem.recent, _ = clearer.clear_old_tool_results(mem.recent, keep=1)
            system, msgs = mem.system(SYSTEM), mem.messages()
        else:
            system, msgs = SYSTEM, msgs + new
            if strategy == "truncate":
                msgs = truncate(msgs, system)
        sizes.append(size(system, msgs))
    seen = (system + json.dumps(msgs)).lower()
    recalled = [c for c in CHECKS if c.lower() in seen]
    return {"strategy": strategy, "peak": max(sizes), "sent": sum(sizes),
            "over_budget_turns": sum(s > BUDGET for s in sizes),
            "recalled": recalled, "system": system, "messages": msgs}

def ask_claude(result):
    import anthropic
    question = "Quick check: what are my name, order ID, city and deadline?"
    r = anthropic.Anthropic().messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=200, system=result["system"],
        messages=result["messages"] + [{"role": "user", "content": question}])
    return "".join(b.text for b in r.content if b.type == "text")

if __name__ == "__main__":
    print(f"{'strategy':<10}{'peak':>8}{'sent (50 turns)':>17}{'over':>6}  recalled")
    for name in ("keep_all", "truncate", "managed"):
        res = run(name)
        print(f"{name:<10}{res['peak']:>8,}{res['sent']:>17,}"
              f"{res['over_budget_turns']:>6}  {len(res['recalled'])}/4 "
              f"{res['recalled']}")
        if "--live" in sys.argv:
            print("   Claude:", ask_claude(res))

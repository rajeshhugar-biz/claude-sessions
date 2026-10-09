"""Simulate a 50-turn support chat and watch the context grow. No API key needed."""
import json

SYSTEM = "You are Acme's support agent. " * 40   # stands in for a long system prompt
TOOLS = [{"name": "search_inventory", "description": "x" * 400}]

def est_tokens(obj):
    """Rough estimate: about 4 characters per token for English text and JSON."""
    text = obj if isinstance(obj, str) else json.dumps(obj)
    return max(1, len(text) // 4)

def build_chat(turns=50, tool_every=3):
    """Return a realistic message list: text turns plus big tool results."""
    msgs = []
    for t in range(1, turns + 1):
        msgs.append({"role": "user", "content": f"Turn {t}: " + "question " * 30})
        if t % tool_every == 0:
            call = {"type": "tool_use", "id": f"toolu_{t}",
                    "name": "search_inventory", "input": {"query": f"item {t}"}}
            rows = [{"sku": f"ACM-{t}-{i}", "stock": i, "notes": "n" * 80}
                    for i in range(30)]
            result = {"type": "tool_result", "tool_use_id": f"toolu_{t}",
                      "content": json.dumps(rows)}
            msgs += [{"role": "assistant", "content": [call]},
                     {"role": "user", "content": [result]}]
        msgs.append({"role": "assistant", "content": "answer " * 60})
    return msgs

def context_tokens(msgs):
    return est_tokens(SYSTEM) + est_tokens(TOOLS) + est_tokens(msgs)

if __name__ == "__main__":
    msgs = build_chat()
    ends = [i for i, m in enumerate(msgs)
            if m["role"] == "assistant" and isinstance(m["content"], str)]
    sent = 0
    for t, end in enumerate(ends, start=1):
        n = context_tokens(msgs[: end + 1])
        sent += n                       # every turn re-sends the whole history
        if t in (1, 10, 20, 30, 40, 50):
            print(f"turn {t:>2}: ~{n:>6,} tokens " + "#" * (n // 2500))
    tool = sum(est_tokens(m) for m in msgs if isinstance(m["content"], list))
    print(f"input tokens sent over {len(ends)} turns: ~{sent:,}")
    print(f"share of history that is tool traffic: {tool / est_tokens(msgs):.0%}")

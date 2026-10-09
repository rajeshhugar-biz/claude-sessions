"""Client-side tool-result clearing: keep only the newest results. No API key."""
import copy
import importlib

PLACEHOLDER = "[cleared to save context - call the tool again if you need this]"

def clear_old_tool_results(messages, keep=3, exclude_tools=()):
    """Return a copy where all but the newest `keep` tool results are replaced."""
    msgs = copy.deepcopy(messages)                    # never edit the caller's list
    names = {b["id"]: b["name"] for m in msgs if isinstance(m["content"], list)
             for b in m["content"] if b.get("type") == "tool_use"}
    results = [b for m in msgs if isinstance(m["content"], list)
               for b in m["content"] if b.get("type") == "tool_result"
               and names.get(b["tool_use_id"]) not in exclude_tools]
    old = results[:-keep] if keep else results
    for block in old:
        block["content"] = PLACEHOLDER                # the tool_use_id stays
    return msgs, len(old)

if __name__ == "__main__":
    sim = importlib.import_module("01_long_chat_simulator")
    chat = sim.build_chat(turns=50)
    trimmed, cleared = clear_old_tool_results(chat, keep=3)
    print(f"cleared {cleared} old tool results")
    print(f"context: ~{sim.context_tokens(chat):,} -> "
          f"~{sim.context_tokens(trimmed):,} tokens")

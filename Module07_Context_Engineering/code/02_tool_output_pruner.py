"""Shrink a tool result before it goes into the context. No API key needed."""
import json
from pathlib import Path

def prune(value, fields=None, max_items=5, max_chars=200):
    """Keep whitelisted keys (at every level), the first few list items, short text."""
    if isinstance(value, dict):
        return {k: prune(v, fields, max_items, max_chars) for k, v in value.items()
                if fields is None or k in fields}
    if isinstance(value, list):
        kept = [prune(v, fields, max_items, max_chars) for v in value[:max_items]]
        if len(value) > max_items:
            kept.append({"_omitted": len(value) - max_items})   # tell Claude
        return kept
    if isinstance(value, str) and len(value) > max_chars:
        return value[:max_chars] + f"...[+{len(value) - max_chars} chars]"
    return value

def to_tool_result(tool_use_id, data, **kw):
    """Compact JSON (no spaces) inside a tool_result block."""
    text = json.dumps(prune(data, **kw), separators=(",", ":"))
    return {"type": "tool_result", "tool_use_id": tool_use_id, "content": text}

if __name__ == "__main__":
    raw = json.loads(Path("data/order_api_response.json").read_text())
    keep = {"order", "id", "status", "shipping", "eta", "tracking_id",
            "items", "name", "qty"}
    block = to_tool_result("toolu_01", raw, fields=keep, max_items=3)
    before, after = len(json.dumps(raw, indent=2)), len(block["content"])
    print(block["content"])
    print(f"~{before // 4:,} tokens -> ~{after // 4:,} tokens")

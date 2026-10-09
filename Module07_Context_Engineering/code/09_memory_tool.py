"""The memory tool: Claude asks for file operations, YOUR code performs them."""
import shutil
from pathlib import Path
import anthropic

ROOT = Path("memory_store").resolve()            # e.g. one folder per end user

def safe_path(virtual):
    """Map /memories/... onto ROOT and refuse anything that escapes it."""
    if virtual != "/memories" and not virtual.startswith("/memories/"):
        raise ValueError("path must be inside /memories")
    if "%2e" in virtual.lower() or "\\" in virtual:
        raise ValueError("suspicious path")
    real = (ROOT / virtual.removeprefix("/memories").lstrip("/")).resolve()
    if real != ROOT and ROOT not in real.parents:  # resolved path left ROOT
        raise ValueError("path escapes /memories")
    return real

def run_memory(cmd):
    """Execute one memory command. Returns the text for the tool_result."""
    op = cmd["command"]
    p = safe_path(cmd.get("path") or cmd["old_path"])
    if op == "view":
        if p.is_dir():
            items = sorted(str(x.relative_to(ROOT)) for x in p.rglob("*"))
            return "\n".join(items) or "(empty directory)"
        lines = p.read_text().splitlines()
        return "\n".join(f"{i:>6}\t{ln}" for i, ln in enumerate(lines, 1))
    if op == "create":
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(cmd["file_text"])
        return f"File created successfully at: {cmd['path']}"
    if op == "str_replace":
        text = p.read_text()
        if text.count(cmd["old_str"]) != 1:
            raise ValueError("old_str must appear exactly once")
        p.write_text(text.replace(cmd["old_str"], cmd.get("new_str", "")))
        return "File edited"
    if op == "insert":
        lines = p.read_text().splitlines()
        lines.insert(cmd["insert_line"], cmd["insert_text"].rstrip("\n"))
        p.write_text("\n".join(lines) + "\n")
        return "Text inserted"
    if op == "delete":
        if p == ROOT:
            raise ValueError("cannot delete the /memories root")
        shutil.rmtree(p) if p.is_dir() else p.unlink()     # dirs: recursive
        return f"Deleted {cmd['path']}"
    if op == "rename":
        new = safe_path(cmd["new_path"])
        if p == ROOT or new.exists():
            raise ValueError("cannot rename root or overwrite a file")
        p.rename(new)
        return f"Renamed to {cmd['new_path']}"
    raise ValueError(f"unknown command {op}")

def run_agent(task, model="claude-sonnet-5-5"):
    client = anthropic.Anthropic()
    tools = [{"type": "memory_20250818", "name": "memory"}]     # no beta header
    messages = [{"role": "user", "content": task}]
    while True:
        r = client.messages.create(model=model, max_tokens=2048,
                                   tools=tools, messages=messages)
        messages.append({"role": "assistant", "content": r.content})
        if r.stop_reason != "tool_use":
            return "".join(b.text for b in r.content if b.type == "text")
        results = []
        for b in r.content:
            if b.type != "tool_use":
                continue
            try:
                out = {"content": run_memory(b.input)}
            except (ValueError, OSError) as e:
                out = {"content": f"Error: {e}", "is_error": True}
            results.append({"type": "tool_result", "tool_use_id": b.id, **out})
        messages.append({"role": "user", "content": results})

if __name__ == "__main__":
    ROOT.mkdir(exist_ok=True)
    print(run_agent("Remember that customer CUS-7781 prefers email follow-ups."))

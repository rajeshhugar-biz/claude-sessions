"""Anthropic-defined CLIENT tool: the text editor. Schema built in, you execute."""
from pathlib import Path

import anthropic

from toolbox import MODEL, tool_result

ROOT = Path(__file__).with_name("workspace").resolve()   # the only place it can edit
EDITOR = {"type": "text_editor_20250728", "name": "str_replace_based_edit_tool",
          "max_characters": 10000}                       # no input_schema needed


def safe_path(p):
    full = (ROOT / p.lstrip("/")).resolve()
    if not full.is_relative_to(ROOT):                    # blocks ../../etc
        raise PermissionError(f"{p} is outside the workspace")
    return full


def handle_editor(cmd):
    """Returns (content, is_error) for view / create / str_replace / insert."""
    try:
        path, action = safe_path(cmd["path"]), cmd["command"]
        if action == "view":
            lines = path.read_text().splitlines()
            return "\n".join(f"{i}: {t}" for i, t in enumerate(lines, 1)), False
        if action == "create":
            path.write_text(cmd["file_text"])
            return f"Created {cmd['path']}", False
        text = path.read_text()
        if action == "str_replace":
            hits = text.count(cmd["old_str"])
            if hits != 1:
                return f"Error: old_str found {hits} times; need exactly 1", True
            path.write_text(text.replace(cmd["old_str"], cmd["new_str"]))
            return "Successfully replaced text at exactly one location.", False
        if action == "insert":
            lines = text.splitlines()
            lines.insert(cmd["insert_line"], cmd["insert_text"])
            path.write_text("\n".join(lines) + "\n")
            return f"Inserted after line {cmd['insert_line']}", False
        return f"Error: unknown command {action}", True
    except (OSError, KeyError, TypeError) as e:          # incl. PermissionError
        return f"Error: {e}", True


if __name__ == "__main__":
    ROOT.mkdir(exist_ok=True)
    (ROOT / "notes.md").write_text("# Return polcy\nReturns accepted for 30 days.\n")
    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": "Fix the spelling in /notes.md"}]
    while True:
        r = client.messages.create(model=MODEL, max_tokens=2048, tools=[EDITOR],
                                   messages=messages)
        messages.append({"role": "assistant", "content": r.content})
        if r.stop_reason != "tool_use":
            break
        messages.append({"role": "user", "content": [
            tool_result(b.id, *handle_editor(b.input))
            for b in r.content if b.type == "tool_use"]})
    print((ROOT / "notes.md").read_text())

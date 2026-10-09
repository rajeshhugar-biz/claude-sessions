"""Client-side compaction: summarise old turns, keep recent turns word for word."""
import json
import re

SUMMARY_PROMPT = """Summarise this conversation for your own future use.
Keep: the user's goal, decisions made, facts (names, IDs, numbers, dates),
open tasks and promises. Drop: greetings, repetition, raw tool output.
Max 200 words. Write it inside <summary></summary> tags."""

def render(messages):
    """Flatten messages to plain text for the summariser."""
    lines = []
    for m in messages:
        c = m["content"]
        text = c if isinstance(c, str) else json.dumps(c)[:500]  # cap tool blobs
        lines.append(f"{m['role'].upper()}: {text}")
    return "\n".join(lines)

def is_plain_user(m):
    """A real user turn: not a tool_result carrier."""
    return m["role"] == "user" and (isinstance(m["content"], str) or not any(
        b.get("type") == "tool_result" for b in m["content"]))

def split_point(messages, keep_last=6):
    """Index where the kept tail starts: a plain user turn, so that
    tool_use / tool_result pairs are never split."""
    i = max(0, len(messages) - keep_last)
    while i > 0 and not is_plain_user(messages[i]):
        i -= 1
    return i

def extract_summary(text):
    m = re.search(r"<summary>(.*?)</summary>", text, re.S)
    return (m.group(1) if m else text).strip()

def compact(messages, summarise, keep_last=6):
    """Replace old turns with one summary; return a new message list."""
    cut = split_point(messages, keep_last)
    if cut == 0:
        return list(messages)                      # nothing old enough to fold
    summary = extract_summary(summarise(render(messages[:cut])))
    first = messages[cut]
    body = first["content"] if isinstance(first["content"], list) else [
        {"type": "text", "text": first["content"]}]
    note = {"type": "text", "text": f"<earlier_conversation_summary>\n{summary}\n"
                                    "</earlier_conversation_summary>"}
    return [{"role": "user", "content": [note, *body]}, *messages[cut + 1:]]

def claude_summariser(client, model="claude-haiku-4-5-20251001"):
    """Your own summariser can use a cheaper model than the chat model."""
    def summarise(transcript):
        r = client.messages.create(
            model=model, max_tokens=1024, system=SUMMARY_PROMPT,
            messages=[{"role": "user",
                       "content": f"<transcript>\n{transcript}\n</transcript>"}])
        return "".join(b.text for b in r.content if b.type == "text")
    return summarise

if __name__ == "__main__":
    demo = [{"role": "user", "content": "Hi, my order ORD-48213 is late."},
            {"role": "assistant", "content": "Sorry! It ships to Pune, ETA Oct 4."},
            {"role": "user", "content": "Can I switch to express?"},
            {"role": "assistant", "content": "Express costs 199 rupees."},
            {"role": "user", "content": "OK, and what about the warranty?"}]
    fake = lambda text: "<summary>Order ORD-48213, Pune, asked about express.</summary>"
    for m in compact(demo, fake, keep_last=1):
        print(m["role"], "->", m["content"])

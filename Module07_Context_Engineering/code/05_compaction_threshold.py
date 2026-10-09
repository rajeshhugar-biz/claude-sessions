import anthropic

client = anthropic.Anthropic()
messages = []

COMPACT = {
    "type": "compact_20260112",
    "trigger": {"type": "input_tokens", "value": 100_000},   # default 150k, min 50k
    "instructions": "Summarise the transcript inside <summary></summary> tags. "
                    "Keep order IDs, decisions and open tasks. Do not call tools.",
}

def chat(user_msg):
    messages.append({"role": "user", "content": user_msg})
    r = client.beta.messages.create(
        betas=["compact-2026-01-12"],
        model="claude-opus-5-5",
        max_tokens=4096,
        messages=messages,
        context_management={"edits": [COMPACT]},
    )
    messages.append({"role": "assistant", "content": r.content})  # keep the block
    if any(b.type == "compaction" for b in r.content):
        print("[compaction ran: earlier turns are now a summary]")
    billed = sum(i.input_tokens for i in (r.usage.iterations or []))
    print(f"[input billed this call, incl. compaction: {billed:,}]")
    return "".join(b.text for b in r.content if b.type == "text")

print(chat("Help me plan a Python service that syncs Acme orders to a CRM."))
print(chat("Add retry logic and a dead-letter queue."))

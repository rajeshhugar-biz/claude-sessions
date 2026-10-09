"""Demo 06: let Claude think - effort on Opus 5.5 vs manual CoT on Haiku 4.5."""
import anthropic

client = anthropic.Anthropic()
QUESTION = ("A team of 12 buys the Pro plan at Rs 999 per seat per month with a "
            "15% discount for 10+ seats. What is the yearly cost?")

# 1) Opus 5.5: thinking is always on. Effort is the dial; ask for the summary.
r = client.messages.create(
    model="claude-opus-5-5", max_tokens=8000,
    thinking={"type": "adaptive", "display": "summarized"},
    output_config={"effort": "medium"},
    messages=[{"role": "user", "content": QUESTION + " Explain briefly."}])
for block in r.content:                      # select blocks by type
    if block.type == "thinking":
        print("THINKING SUMMARY:", block.thinking[:300])
    elif block.type == "text":
        print("ANSWER:", block.text)

# 2) Haiku 4.5 with thinking off: manual chain of thought, answer in tags.
r = client.messages.create(
    model="claude-haiku-4-5-20251001", max_tokens=1024,
    messages=[{"role": "user", "content": QUESTION + " Work through it step "
               "by step, then give the final figure in <answer></answer> tags."}])
print("HAIKU:", "".join(b.text for b in r.content if b.type == "text"))

"""Demo 01: the same task, written vague and then clear and direct."""
import anthropic

client = anthropic.Anthropic()


def ask(prompt):
    r = client.messages.create(model="claude-sonnet-5-5", max_tokens=1024,
                               output_config={"effort": "low"},
                               messages=[{"role": "user", "content": prompt}])
    return "".join(b.text for b in r.content if b.type == "text")


vague = "Write something about our refund policy."

clear = """Write a reply to a customer who asks how refunds work.
Audience: a first-time buyer on Nimbus Learning, not technical.
Why: this text goes into our help-centre chat, so it must be short and exact.
Facts: full refund within 14 days if less than 30% of the course is watched.
Format: 3 sentences of plain prose, no headings, no bullet points.
End by telling them where to click: Account > Orders > Request refund."""

for name, prompt in [("VAGUE", vague), ("CLEAR", clear)]:
    print(f"--- {name} ---\n{ask(prompt)}\n")

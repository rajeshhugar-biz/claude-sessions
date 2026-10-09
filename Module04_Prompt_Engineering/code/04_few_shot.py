"""Demo 04: few-shot examples in <examples> tags (relevant, diverse, structured)."""
import anthropic

client = anthropic.Anthropic()

EXAMPLES = [
    ("Charged in USD instead of INR on my last invoice.", "billing"),
    ("Quiz timer freezes at 0:00 on Safari, so I can't submit.", "technical"),
    ("I got married. Please show my new surname on future certificates.", "account"),
    ("The chart in Lesson 2 labels the axes the wrong way round.", "content"),
    ("Love the new layout! Any plans for a dark mode?", "other"),
]
examples = "\n".join(
    f"<example>\n<ticket>{t}</ticket>\n<label>{label}</label>\n</example>"
    for t, label in EXAMPLES)

system = ("You route Nimbus Learning support tickets. Labels: billing, technical, "
          "account, content, other.\n\n<examples>\n" + examples + "\n</examples>\n\n"
          "Answer with the label in <label></label> tags only.")

for ticket in ["Refund please, I bought the wrong course.",
               "Video player shows a black screen on Firefox."]:
    r = client.messages.create(model="claude-sonnet-5-5", max_tokens=1024,
                               output_config={"effort": "low"}, system=system,
                               messages=[{"role": "user",
                                          "content": f"<ticket>{ticket}</ticket>"}])
    print(ticket, "->", "".join(b.text for b in r.content if b.type == "text"))

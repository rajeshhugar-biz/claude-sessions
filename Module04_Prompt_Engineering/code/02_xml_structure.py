"""Demo 02: separate context, input and instructions with XML tags."""
import re
import anthropic

client = anthropic.Anthropic()

# Fixed demo text. For real user input, sanitise it first (see 08).
ticket = "Charged twice for Pro this month. Also the app logs me out every hour."

prompt = f"""<context>
Nimbus Learning sells online courses. Support has three teams:
billing, technical and account.
</context>

<ticket>
{ticket}
</ticket>

<instructions>
List each separate issue in the ticket and the team that should own it.
Put the list in <issues> tags, then a one-line summary for the team lead
in <summary> tags.
</instructions>"""

r = client.messages.create(model="claude-sonnet-5-5", max_tokens=1024,
                           messages=[{"role": "user", "content": prompt}])
text = "".join(b.text for b in r.content if b.type == "text")
summary = re.search(r"<summary>(.*?)</summary>", text, re.S)
print("SUMMARY ->", summary.group(1).strip() if summary else "(not found)")

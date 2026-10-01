import anthropic
from dotenv import load_dotenv
load_dotenv()  # loads ANTHROPIC_API_KEY from .env
client = anthropic.Anthropic()

SYSTEM = "Classify customer messages as positive, negative or neutral. Reply with one word."

EXAMPLES = """<examples>
<example><input>Loved the new update!</input><label>positive</label></example>
<example><input>App crashes every time I log in.</input><label>negative</label></example>
<example><input>How do I change my email?</input><label>neutral</label></example>
</examples>"""

def classify(text):
    r = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=5,
        system=SYSTEM,
        messages=[{"role": "user",
                   "content": f"{EXAMPLES}\n\n<input>{text}</input>"}],
    )
    return r.content[0].text.strip()

print(classify("Refund took three weeks. Not happy."))
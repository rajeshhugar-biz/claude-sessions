import anthropic
from dotenv import load_dotenv
load_dotenv()  # loads ANTHROPIC_API_KEY from .env
client = anthropic.Anthropic()

SYSTEM = ("Classify customer messages as positive, negative or neutral. "
          "Reply with one word.")
EXAMPLES = """<examples>
<example><input>Loved the new update!</input><label>positive</label></example>
<example><input>Great, another update that breaks everything.</input><label>negative</label></example>
<example><input>How do I change my email?</input><label>neutral</label></example>
<example><input>Delivery was late but the staff were lovely.</input><label>positive</label></example>
</examples>"""

TEST = [
    ("Wow, thanks for charging me twice. Brilliant.", "negative"),
    ("Where can I download my invoice?", "neutral"),
    ("Honestly the best support I've had anywhere.", "positive"),
    ("It works, I guess.", "neutral"),
    ("WHY IS MY ORDER STILL NOT HERE???", "negative"),
    ("Can someone call me back about my plan?", "neutral"),
    ("Slow app, but the new dark mode is gorgeous.", "positive"),
    ("Cancel my subscription.", "neutral"),
    ("Five stars. Would recommend to my whole family.", "positive"),
    ("Oh great, the app logged me out again.", "negative"),
]

def classify(text, shots):
    content = (EXAMPLES + "\n\n" if shots else "") + f"<input>{text}</input>"
    r = client.messages.create(model="claude-haiku-4-5-20251001", max_tokens=5,
                               system=SYSTEM,
                               messages=[{"role": "user", "content": content}])
    return r.content[0].text.strip().lower(), r.usage.input_tokens

for shots in (False, True):
    correct, tokens = 0, 0
    for text, gold in TEST:
        label, used = classify(text, shots)
        correct += (label == gold)
        tokens += used
    name = "few-shot" if shots else "zero-shot"
    print(f"{name:<10} accuracy {correct}/{len(TEST)}  input tokens {tokens}")
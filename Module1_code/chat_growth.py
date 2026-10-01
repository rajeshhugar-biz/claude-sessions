import anthropic
from dotenv import load_dotenv
load_dotenv() # loads ANTHROPIC_API_KEY from .env into the environment
client = anthropic.Anthropic()

history = []

def chat(user_msg):
    history.append({"role": "user", "content": user_msg})
    r = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=1024,
        messages=history,
    )
    history.append({"role": "assistant", "content": r.content})
    print(f"[input tokens this turn: {r.usage.input_tokens}]")
    return "".join(b.text for b in r.content if b.type == "text")

print(chat("My name is Priya and I teach Python."))
print(chat("What's my name and what do I teach?"))
import anthropic
client = anthropic.Anthropic()

QUESTIONS = [
    "I'm planning a 3-day trip to Jaipur. Where should I start?",
    "What should I see on day 1?",
    "And day 2?",
    "Suggest local food for each day.",
    "What's a good budget per day in rupees?",
    "Which of these places are best at sunset?",
    "What should I pack in October?",
    "Any etiquette tips for temples?",
    "Summarise the whole plan in 5 bullets.",
    "Which day would you cut if I only had 2 days?",
]

history, total = [], 0
print(f"{'turn':>4} {'input_tokens':>13} {'output_tokens':>14}")
for i, q in enumerate(QUESTIONS, 1):
    history.append({"role": "user", "content": q})
    r = client.messages.create(model="claude-sonnet-5-5", max_tokens=600,
                               messages=history)
    history.append({"role": "assistant", "content": r.content})
    total += r.usage.input_tokens
    print(f"{i:>4} {r.usage.input_tokens:>13} {r.usage.output_tokens:>14}")
print("total input tokens:", total)
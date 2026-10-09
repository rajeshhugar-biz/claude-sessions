import time, anthropic
client = anthropic.Anthropic()

PUZZLE = ("Five friends sit in a row. Chirag is at the left end and "
          "Divya is at the right end. Asha is not at either end. "
          "Ben sits immediately to the right of Asha. "
          "Esha is not next to Divya. Give the order left to right.")

for effort in ("low", "medium", "high"):
    t0 = time.perf_counter()
    r = client.messages.create(
        model="claude-sonnet-5-5", max_tokens=16000,
        thinking={"type": "adaptive"},
        output_config={"effort": effort},
        messages=[{"role": "user", "content": PUZZLE}],
    )
    secs = time.perf_counter() - t0
    answer = "".join(b.text for b in r.content if b.type == "text")
    cost = (r.usage.input_tokens * 2 + r.usage.output_tokens * 10) / 1e6
    print(f"{effort:<7} out={r.usage.output_tokens:<6} {secs:5.1f}s ${cost:.4f}")
    print("   ", answer.strip()[:120])
"""Lab 3: classify tickets with the Batch API and compare cost with real-time calls."""
import json
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-haiku-4-5-20251001"
SYSTEM = ("Label the support ticket as billing, account, bug or other. "
          "Reply with one word.")

TEMPLATES = ["I was charged twice for order {n}.",
             "How do I change my email? ({n})",
             "App crashes on the statements page ({n}).",
             "Do you have a job opening? ({n})"]
tickets = {f"t-{n:03d}": TEMPLATES[n % 4].format(n=n) for n in range(200)}

# 1. Estimate tokens for one request (free endpoint)
sample = client.messages.count_tokens(
    model=MODEL, system=SYSTEM,
    messages=[{"role": "user", "content": tickets["t-000"]}],
)
est_in, est_out = sample.input_tokens * len(tickets), 3 * len(tickets)
realtime = (est_in * 1 + est_out * 5) / 1e6     # Haiku 4.5: $1 in / $5 out
print(f"Estimated real-time cost ${realtime:.4f}; batch (50% off) ${realtime/2:.4f}")

# 2. Submit the batch
batch = client.messages.batches.create(requests=[
    {"custom_id": tid, "params": {"model": MODEL, "max_tokens": 5, "system": SYSTEM,
                                  "messages": [{"role": "user", "content": text}]}}
    for tid, text in tickets.items()
])
json.dump({"batch_id": batch.id}, open("batch.json", "w"))
print("Submitted", batch.id, "- run 14_batch_results.py", batch.id, "later")

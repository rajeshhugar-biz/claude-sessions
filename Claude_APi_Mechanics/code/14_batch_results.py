import sys, time
import anthropic

client = anthropic.Anthropic()
batch_id = sys.argv[1]                           # msgbatch_...

while True:
    batch = client.messages.batches.retrieve(batch_id)
    print("status:", batch.processing_status, batch.request_counts)
    if batch.processing_status == "ended":
        break
    time.sleep(60)                               # poll gently

for result in client.messages.batches.results(batch_id):   # order NOT guaranteed
    if result.result.type == "succeeded":
        msg = result.result.message
        label = "".join(b.text for b in msg.content if b.type == "text").strip()
        print(result.custom_id, "->", label)
    else:                                        # errored / canceled / expired
        print(result.custom_id, "failed:", result.result.type)

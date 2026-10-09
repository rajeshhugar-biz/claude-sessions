import anthropic

client = anthropic.Anthropic()

tickets = {
    "t-001": "My card was charged twice for one order.",
    "t-002": "How do I update my address?",
    "t-003": "The app crashes when I open statements.",
}

batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": ticket_id,                 # your key to match results
            "params": {
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 10,
                "system": "Label the ticket: billing, account or bug. One word.",
                "messages": [{"role": "user", "content": text}],
            },
        }
        for ticket_id, text in tickets.items()
    ]
)
print(batch.id, batch.processing_status)       # msgbatch_..., in_progress

"""Ask a question about the invoice and get answers tied to exact source text."""
import anthropic

client = anthropic.Anthropic()
with open("invoice_nimbus.txt", encoding="utf-8") as f:
    invoice = f.read()

response = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": [
        {"type": "document",
         "source": {"type": "text", "media_type": "text/plain", "data": invoice},
         "title": "Invoice NL-2026-0412",
         "citations": {"enabled": True}},  # can't combine with output_config.format
        {"type": "text", "text": "What is the payment due date and the total?"},
    ]}],
)
for block in response.content:
    if block.type != "text":
        continue
    print(block.text, end="")
    for c in block.citations or []:
        print(f'  [source: "{c.cited_text.strip()}"]', end="")
print()

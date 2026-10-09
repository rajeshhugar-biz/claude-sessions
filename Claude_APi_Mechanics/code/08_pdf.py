import base64
import anthropic

client = anthropic.Anthropic()

with open("annual_report.pdf", "rb") as f:
    pdf_b64 = base64.standard_b64encode(f.read()).decode("utf-8")

response = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=2048,
    messages=[{
        "role": "user",
        "content": [
            {"type": "document", "source": {
                "type": "base64", "media_type": "application/pdf", "data": pdf_b64}},
            {"type": "text", "text": "Summarise revenue trends. Cite page numbers."},
        ],
    }],
)
print("".join(b.text for b in response.content if b.type == "text"))
print("input tokens:", response.usage.input_tokens)

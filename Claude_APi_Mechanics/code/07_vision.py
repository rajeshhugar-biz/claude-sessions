import base64
import anthropic

client = anthropic.Anthropic()

with open("receipt.png", "rb") as f:
    receipt_b64 = base64.standard_b64encode(f.read()).decode("utf-8")

response = client.messages.create(
    model="claude-sonnet-5-5",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Image 1:"},
            {"type": "image", "source": {
                "type": "base64", "media_type": "image/png", "data": receipt_b64}},
            {"type": "text", "text": "Image 2:"},
            {"type": "image", "source": {
                "type": "url",
                "url": "https://platform.claude.com/docs/images/vision-example.jpg"}},
            {"type": "text", "text": "What is the total on Image 1? Describe Image 2."},
        ],
    }],
)
print("".join(b.text for b in response.content if b.type == "text"))

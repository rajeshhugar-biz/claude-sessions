import anthropic

client = anthropic.Anthropic()

# 1. Upload once
with open("annual_report.pdf", "rb") as f:
    uploaded = client.files.upload(file=("annual_report.pdf", f, "application/pdf"))
print("file id:", uploaded.id)

# 2. Reference by file_id in as many requests as you like
for question in ["What were the three biggest risks?", "List all subsidiaries."]:
    r = client.messages.create(
        model="claude-sonnet-5-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": [
            {"type": "document", "source": {"type": "file", "file_id": uploaded.id}},
            {"type": "text", "text": question},
        ]}],
    )
    print(question, "->", "".join(b.text for b in r.content if b.type == "text")[:200])

# 3. Clean up when done
client.files.delete(uploaded.id)

"""Lab 2: ask many questions about one PDF, using the Files API and prompt caching."""
import sys
import anthropic

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"
BASE_IN = 2.0                                    # USD per 1M input tokens
WRITE, READ = 1.25 * BASE_IN, 0.1 * BASE_IN      # 5-minute cache write / read

pdf_path = sys.argv[1] if len(sys.argv) > 1 else "annual_report.pdf"
with open(pdf_path, "rb") as f:
    file_id = client.files.upload(file=(pdf_path, f, "application/pdf")).id

questions = [
    "Give a 3-bullet summary of this document.",
    "What numbers are reported for revenue?",
    "List any risks mentioned.",
    "Who is the intended audience?",
]

cost_cached = cost_uncached = 0.0
for q in questions:
    r = client.messages.create(
        model=MODEL, max_tokens=400,
        messages=[{"role": "user", "content": [
            {"type": "document", "source": {"type": "file", "file_id": file_id},
             "cache_control": {"type": "ephemeral"}},
            {"type": "text", "text": q},
        ]}],
    )
    u = r.usage
    total_in = u.input_tokens + u.cache_creation_input_tokens + u.cache_read_input_tokens
    cost_cached += (u.input_tokens * BASE_IN + u.cache_creation_input_tokens * WRITE
                    + u.cache_read_input_tokens * READ) / 1e6
    cost_uncached += total_in * BASE_IN / 1e6
    print(f"\nQ: {q}\n   write={u.cache_creation_input_tokens} "
          f"read={u.cache_read_input_tokens} uncached={u.input_tokens}")

print(f"\nInput cost with caching:    ${cost_cached:.4f}")
print(f"Input cost without caching: ${cost_uncached:.4f}")
client.files.delete(file_id)

"""Demo 03: long documents first, question last, answer grounded in quotes."""
from pathlib import Path
import anthropic

client = anthropic.Anthropic()
DATA = Path(__file__).parent / "data"

docs = []
for i, path in enumerate(sorted(DATA.glob("*.txt")), start=1):
    docs.append(f'<document index="{i}">\n<source>{path.name}</source>\n'
                f"<document_content>\n{path.read_text()}\n</document_content>\n"
                "</document>")

question = "A learner watched 40% of a course 10 days ago. Can they get a refund?"

prompt = ("<documents>\n" + "\n".join(docs) + "\n</documents>\n\n"
          "First, copy the sentences from the documents that are relevant to the "
          "question into <quotes> tags. Then answer in <answer> tags, using only "
          "those quotes. If the documents do not answer it, say so.\n\n"
          f"Question: {question}")

r = client.messages.create(model="claude-sonnet-5-5", max_tokens=2048,
                           messages=[{"role": "user", "content": prompt}])
print("".join(b.text for b in r.content if b.type == "text"))

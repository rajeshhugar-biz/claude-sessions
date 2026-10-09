"""Lab 2: retrieval quality vs chunk size: is the answer in the top 1 / top 3
chunks, and how many tokens do those chunks add to the prompt? No API key."""
import importlib
from pathlib import Path

rag = importlib.import_module("10_local_rag")

# (question, section that must be retrieved, phrase the answer needs)
TESTS = [
    ("If I paid by UPI, when do I get my money back?", "Returns and refunds",
     "5 to 7"),
    ("Is there a fee for returning an opened mixer I don't like?",
     "Returns and refunds", "10 percent"),
    ("How long is the compressor covered on a fridge?", "Warranty", "ten-year"),
    ("Can I change the address after my order has shipped?", "Order status",
     "cannot be changed"),
    ("How much does express delivery cost?", "Delivery times", "199 rupees"),
    ("What is the visit fee outside warranty?", "Service visits", "399"),
    ("How much is extra copper pipe for an AC?", "Installation", "650"),
    ("What should I do if the product gives an electric shock?", "Escalation",
     "safety desk"),
    ("Can I pay in monthly instalments?", "Payments and invoices", "No-cost EMI"),
    ("Can an agent read out the full phone number?", "Privacy rules for agents",
     "last four digits"),
]

def evaluate(max_words, overlap):
    text = Path("data/acme_handbook.md").read_text()
    chunks = rag.chunk_markdown(text, "acme_handbook.md", max_words, overlap)
    retriever = rag.Retriever(chunks)
    at1 = at3 = prompt_tokens = 0
    for question, section, phrase in TESTS:
        top = [c for _, c in retriever.top_k(question, k=3)]
        at1 += phrase in top[0]["text"]
        at3 += any(phrase in c["text"] for c in top)
        prompt_tokens += sum(len(c["text"]) // 4 for c in top)
    n = len(TESTS)
    return len(chunks), at1 / n, at3 / n, prompt_tokens // n

if __name__ == "__main__":
    print(f"{'words':>6}{'overlap':>8}{'chunks':>8}{'answer@1':>10}{'answer@3':>10}"
          f"{'tokens@3':>10}")
    for words, overlap in [(30, 0), (30, 10), (60, 15), (120, 30), (400, 0)]:
        n, a1, a3, tok = evaluate(words, overlap)
        print(f"{words:>6}{overlap:>8}{n:>8}{a1:>10.0%}{a3:>10.0%}{tok:>10}")

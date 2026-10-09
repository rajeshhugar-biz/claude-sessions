"""Tiny local RAG: chunk -> vectorise (TF-IDF) -> top-k retrieval. No API key."""
import re
from pathlib import Path
import numpy as np

try:                                   # use scikit-learn if it is installed
    from sklearn.feature_extraction.text import TfidfVectorizer
except ImportError:                    # otherwise the numpy version below
    TfidfVectorizer = None

STOP = set("a an and are as at be by can do does for from how if in is it of on "
           "or the their to what when with".split())

def chunk_markdown(text, source, max_words=60, overlap=15):
    """Split by '## ' headings, then into overlapping word windows.
    Each chunk keeps its source and heading as metadata."""
    chunks = []
    for section in re.split(r"\n(?=## )", text):
        heading = section.splitlines()[0].lstrip("# ").strip()
        words = section.split()
        step = max_words - overlap
        for start in range(0, max(1, len(words) - overlap), step):
            chunks.append({"id": len(chunks), "source": source, "heading": heading,
                           "text": " ".join(words[start:start + max_words])})
    return chunks

def tokenize(text):
    """Lower-case words, drop stop words, crude plural folding (refunds -> refund)."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w[:-1] if len(w) > 3 and w.endswith("s") else w
            for w in words if w not in STOP]

def tfidf_matrix(docs):
    """Plain numpy TF-IDF with L2-normalised rows (so dot product = cosine)."""
    vocab = {w: i for i, w in enumerate(sorted({w for d in docs for w in tokenize(d)}))}
    tf = np.zeros((len(docs), len(vocab)))
    for r, d in enumerate(docs):
        for w in tokenize(d):
            tf[r, vocab[w]] += 1
    idf = np.log((1 + len(docs)) / (1 + (tf > 0).sum(axis=0))) + 1
    m = tf * idf
    return m / np.linalg.norm(m, axis=1, keepdims=True).clip(min=1e-12), vocab, idf

class Retriever:
    def __init__(self, chunks, use_sklearn=True):
        self.chunks = chunks
        texts = [f"{c['heading']} {c['text']}" for c in chunks]
        self.vec = TfidfVectorizer(tokenizer=tokenize, token_pattern=None) if (
            use_sklearn and TfidfVectorizer) else None
        if self.vec:
            self.matrix = self.vec.fit_transform(texts).toarray()   # L2-normalised
        else:
            self.matrix, self.vocab, self.idf = tfidf_matrix(texts)

    def embed_query(self, query):
        if self.vec:
            return self.vec.transform([query]).toarray()[0]
        v = np.zeros(len(self.vocab))
        for w in tokenize(query):
            if w in self.vocab:
                v[self.vocab[w]] += 1
        v *= self.idf
        n = np.linalg.norm(v)
        return v / n if n else v

    def top_k(self, query, k=3):
        scores = self.matrix @ self.embed_query(query)       # cosine similarity
        best = np.argsort(scores)[::-1][:k]
        return [(float(scores[i]), self.chunks[i]) for i in best]

if __name__ == "__main__":
    text = Path("data/acme_handbook.md").read_text()
    chunks = chunk_markdown(text, source="acme_handbook.md")
    print(f"{len(chunks)} chunks")
    rag = Retriever(chunks)
    for score, c in rag.top_k("How long does a UPI refund take?", k=3):
        print(f"{score:.2f}  [{c['heading']}]  {c['text'][:70]}...")

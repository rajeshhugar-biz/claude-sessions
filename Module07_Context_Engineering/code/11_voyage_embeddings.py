"""Optional: real embeddings with Voyage AI (Anthropic has no embedding model).
Needs: pip install -U voyageai   and   VOYAGE_API_KEY (from MongoDB Atlas)."""
import importlib
from pathlib import Path
import numpy as np
import voyageai

rag = importlib.import_module("10_local_rag")
vo = voyageai.Client()                       # reads VOYAGE_API_KEY

chunks = rag.chunk_markdown(Path("data/acme_handbook.md").read_text(),
                            source="acme_handbook.md")
texts = [f"{c['heading']}\n{c['text']}" for c in chunks]
doc_vecs = np.array(vo.embed(texts, model="voyage-4",
                             input_type="document").embeddings)

query = "How long does a UPI refund take?"
q_vec = np.array(vo.embed([query], model="voyage-4",
                          input_type="query").embeddings[0])

scores = doc_vecs @ q_vec                   # Voyage vectors are length 1: dot = cosine
for i in np.argsort(scores)[::-1][:3]:
    print(f"{scores[i]:.3f}  [{chunks[i]['heading']}]")

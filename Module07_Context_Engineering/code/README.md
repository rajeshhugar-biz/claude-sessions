# Module 7 · Context Engineering · code pack

Python 3.10+. Run every command from this `code/` folder.

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install "anthropic>=1.0" numpy scikit-learn         # scikit-learn is optional
export ANTHROPIC_API_KEY=...                            # only for the API demos
python -m unittest discover -s tests -v                 # 19 tests, no API key needed
```

Files marked **offline** run without an API key. Token counts in the offline files are
estimates (about 4 characters per token). Use `client.messages.count_tokens(...)` for
exact numbers.

| File | What it shows | Slide |
|---|---|---|
| `01_long_chat_simulator.py` | **Offline.** Builds a 50-turn chat with tool calls and prints how the context grows and how much input is re-sent | 10 |
| `02_tool_output_pruner.py` | **Offline.** Shrinks a verbose order-API response: whitelisted fields, capped lists, short strings, compact JSON | 14 |
| `03_clear_old_results.py` | **Offline.** Client-side clearing of old tool results (keeps the newest N, supports excluded tools) | 15 |
| `04_summarise_helpers.py` | **Offline demo** + optional Claude summariser. Client-side compaction that never splits a tool_use / tool_result pair | 19 |
| `05_compaction_threshold.py` | API. Server-side compaction at a token threshold (`compact_20260112`, beta `compact-2026-01-12`) | 22 |
| `06_compaction_on_demand.py` | API. On-demand compaction (`compaction={"type": "summarize"}`, beta `compact-2026-09-04`) | 23 |
| `07_context_editing.py` | API. Context editing: `clear_thinking_20251015` + `clear_tool_uses_20250919` (beta `context-management-2025-06-27`) | 25 |
| `08_window_memory.py` | **Offline.** `WindowMemory`: running summary in the system prompt + last N messages verbatim | 30 |
| `09_memory_tool.py` | API. The memory tool (`memory_20250818`) with a hand-written, path-safe handler and agent loop | 32 |
| `10_local_rag.py` | **Offline.** Chunking with overlap + TF-IDF (scikit-learn if installed, else numpy) + top-k cosine retrieval | 36 |
| `11_voyage_embeddings.py` | Optional. Same retrieval with Voyage AI embeddings (`pip install -U voyageai`, `VOYAGE_API_KEY`) | 35 |
| `12_rag_prompt.py` | API (or `--dry-run` offline). Puts only the top-3 chunks into the prompt, documents first, question last | 37 |
| `13_subagent_isolation.py` | API. Subagents read raw material in their own context; the lead agent sees only short reports | 41 |
| `lab1_degrading_chat.py` | **Offline** (+ `--live`). Lab 1: 50-turn chat, three strategies: keep all, truncate, managed | 45 |
| `lab2_rag_eval.py` | **Offline.** Lab 2: answer@1 / answer@3 / prompt tokens for different chunk sizes | 45 |
| `tests/test_context_tools.py` | Unit tests for the offline pieces and the memory handler's path checks | - |
| `data/acme_handbook.md` | Fictional support handbook used by the RAG demos | - |
| `data/order_api_response.json` | Fictional, deliberately verbose order API response | - |

Notes

- Beta features (compaction, context editing) use `client.beta.messages.create(..., betas=[...])`.
  Names and headers are as documented in October 2026; check the docs before each cohort.
- `09_memory_tool.py` writes to `./memory_store/`. Delete the folder to reset the agent's memory.
- All company names, people and IDs in this pack are fictional.

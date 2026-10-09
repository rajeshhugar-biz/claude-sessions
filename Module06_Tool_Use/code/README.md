# Module 6 · Tool Use — code pack

Python 3.10+ and the `anthropic` SDK 1.x. All company, customer and order data is fictional
(Nimbus Outdoor, an imaginary online store).

## Setup

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install anthropic
export ANTHROPIC_API_KEY=sk-ant-...                     # Windows: set ANTHROPIC_API_KEY=...
python setup_db.py                                      # creates shop.db (re-run to reset)
python -m unittest -v test_toolbox.py                   # 28 offline tests, no API key needed
```

Run every file from this folder. `setup_db.py` also resets refunds made during class.

## Files

| File | What it shows | Slide | Needs API key |
|---|---|---|---|
| `setup_db.py` | Creates `shop.db` (SQLite): customers, orders, refunds | 16 | No |
| `toolbox.py` | Shared tools (weather, calculator, orders DB, refund), their definitions, the dispatcher `run_tool()` | 16, 36 | No |
| `01_tool_design.py` | A linter for tool definitions (name, description, schema) | 17 | No |
| `02_tool_choice.py` | `auto`, `none`, `disable_parallel_tool_use`, forced `tool`; guard for models that reject forcing | 22 | Yes |
| `03_strict_tool.py` | `strict: true` tool; schema-valid is not the same as correct | 24 | Yes |
| `04_agent_loop.py` | Hand-built multi-step loop with stopping conditions | 28 | Yes |
| `05_parallel_calls.py` | Run independent calls concurrently, answer all in one user turn | 30 | Yes |
| `06_tool_errors.py` | What Claude receives for seven kinds of failure (`is_error`) | 37 | No |
| `07_approval_gate.py` | Human approval before `issue_refund` runs | 43 | Yes |
| `08_web_search.py` | Server tool: web search with `max_uses`, domains, location, `pause_turn` | 49 | Yes |
| `09_fetch_and_code.py` | Server tools: web fetch + code execution in one request | 51 | Yes |
| `10_text_editor_tool.py` | Anthropic-defined client tool (text editor) with a sandboxed handler | 53 | Yes |
| `11_tool_runner.py` | SDK tool runner (beta): `@beta_tool` + `client.beta.messages.tool_runner` | 56 | Yes |
| `test_toolbox.py` | Unit tests: tools, dispatcher, gates, editor handler, agent loop with a fake client | 39 | No |
| `lab1_support_agent.py` | Lab 1 solution: support chat agent, hand-built loop, cost meter | 61 | Yes |
| `lab2_refund_guardrails.py` | Lab 2 solution: policy check + human approval + audit log | 61 | Yes |
| `lab3_tool_runner_port.py` | Lab 3 solution: Lab 1 rebuilt on the tool runner | 61 | Yes |

## Notes

- Demos use `claude-sonnet-5-5` (`toolbox.MODEL`). Change it in one place.
- Claude Opus 5.5, Sonnet 5.5 and Fable 5.1 accept only `tool_choice` `auto` or `none`;
  `02_tool_choice.py` uses Claude Haiku 4.5 to show a forced tool call.
- Web search costs $10 per 1,000 searches plus tokens; an org admin can disable it in the
  Claude Console. Web fetch has no extra charge. Code execution is free when the request also
  has `web_search_20260209`/`web_fetch_20260209` or later (as of October 2026).
- `10_text_editor_tool.py` creates a `workspace/` folder and edits only inside it.
- `lab2_refund_guardrails.py` appends to `refund_audit.jsonl`.

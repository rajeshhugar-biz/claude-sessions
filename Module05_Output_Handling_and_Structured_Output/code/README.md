# Module 5 code pack: Output handling and structured output

All company names and invoice data are fictional.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install anthropic pydantic pillow
export ANTHROPIC_API_KEY=sk-ant-...                   # Windows: set ANTHROPIC_API_KEY=...
cd code
python -m unittest -v        # 30 offline tests, no API key needed
```

Run every file from inside `code/`. The helper modules are imported by name.
Tested with `anthropic` 1.9 and `pydantic` 2.13, Python 3.10+.

## Files

| File | Needs API key | What it shows | Slide |
|---|---|---|---|
| `01_json_outputs.py` | yes | JSON outputs with a raw JSON schema in `output_config.format` | 9 |
| `02_parse_pydantic.py` | yes | `client.messages.parse()` with a Pydantic model, `parsed_output` | 10 |
| `03_tool_extraction.py` | yes | Tool-based extraction: `strict: true` tool + forced `tool_choice` (Haiku 4.5) | 12 |
| `invoice_models.py` | no | Pydantic `Invoice` / `LineItem` models: required, nullable, optional | 19 |
| `04_show_schema.py` | no | Prints the schema the SDK actually sends (`transform_schema`) | 17, 19 |
| `retry_extract.py` | no | `extract_with_retry()`: validate, apply rules, feed errors back, retry | 22 |
| `05_retry_demo.py` | no | The retry loop with a fake client: fails twice, succeeds on attempt 3 | 22 |
| `safe_json.py` | no | `extract_json()`: defensive parser for fences, prose, truncation | 25 |
| `06_messy_outputs.py` | no | Runs the parser over eight realistic messy replies | 24, 25 |
| `checks.py` | no | Business rules: recompute line totals, subtotal, tax, total; grounding | 28 |
| `07_cross_check.py` | no | A confident, schema-valid extraction that is still wrong | 28 |
| `08_citations.py` | yes | Citations: answers tied to exact source text | 29 |
| `lab1_starter.py` | yes | Lab starter with TODOs | 32 |
| `lab1_invoice_extractor.py` | yes | Lab solution: text or PNG invoice to validated JSON with auto-retry | 32 |
| `test_safe_json.py` | no | 15 unit tests for the defensive parser | 25 |
| `test_retry_extract.py` | no | 9 tests for the retry loop (fake client; checks kwargs against the SDK) | 22 |
| `test_checks.py` | no | 6 tests for the business rules | 28 |
| `make_invoice.py` | no | Regenerates `invoice_nimbus.txt` and `invoice_nimbus.png` | – |
| `invoice_nimbus.txt` / `.png` | – | The fictional sample invoice (INR, GST 18%) | 32 |
| `sample_extraction.json` | – | A "confident" model output with two wrong numbers | 27, 28 |

## Notes (as of October 2026)

- Structured outputs: `output_config={"format": {"type": "json_schema", "schema": {...}}}`.
  The old `output_format` request parameter and the beta header are deprecated.
  In the Python SDK, `output_format=` is still the argument name for a Pydantic type
  on `client.messages.parse()` only.
- Claude Opus 5.5, Sonnet 5.5 and Fable 5.1 reject forced `tool_choice`
  (`any` / `tool`) with a 400. That is why `03_tool_extraction.py` uses Haiku 4.5.
  On the 5.5 models, use structured outputs, or `auto` plus a strict tool.
- Structured outputs and citations cannot be combined in one request (400).

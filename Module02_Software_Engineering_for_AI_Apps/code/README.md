# Module 2 code pack: Software Engineering for AI Apps

Python 3.10+. Run every file from this `code/` folder.

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt                        # anthropic, httpx, pydantic
export ANTHROPIC_API_KEY=...                           # only for files marked API
python -m unittest discover -s tests -v                # offline tests, no key needed
```

| File | Needs key? | What it shows | Slide |
|---|---|---|---|
| `01_http_anatomy.py` | no | Builds (does not send) the HTTP request behind a Claude call | 11 |
| `02_status_policy.py` | no | Status code -> action: success, retry, or fix | 12 |
| `03_json_roundtrip.py` | no | `json.dumps` / `json.loads`, types that do not survive | 17 |
| `04_pydantic_validate.py` | no | Validating model output with Pydantic; reading `ValidationError` | 19 |
| `05_structured_output.py` | API | `client.messages.parse(output_format=PydanticModel)` | 20 |
| `06_raw_httpx.py` | API | A Claude call with plain httpx: headers, JSON body, errors | 24 |
| `07_sdk_call.py` | API | The same call with the `anthropic` SDK | 25 |
| `08_async_basics.py` | no | Sequential vs `asyncio.gather` with fake 1-second calls | 30 |
| `09_backoff.py` | no | Exponential backoff with full jitter + async retry helper | 33 |
| `10_async_claude.py` | API | `AsyncAnthropic` + `gather` + `Semaphore` + backoff + retry-after | 34 |
| `11_fake_client.py` | no | Same concurrency pattern against a fake client (testing) | 35 |
| `12_sse_parser.py` | no | Parses `sse_sample.txt`, a stream in the documented SSE format | 40 |
| `13_code_review.py` | API | Claude reviews `sample_diff.patch`; findings come back as JSON | 56 |
| `ci.yml` | no | GitHub Actions workflow: compile + offline tests, then a staging smoke call | 51 |

## Labs (slide 61)

| Lab | Solution | Notes |
|---|---|---|
| 1 Raw HTTP vs SDK | `lab1_raw_vs_sdk.py` | API. Retry helper is tested offline with `httpx.MockTransport` |
| 2 Async pipeline | `lab2_async_pipeline.py` | `--fake` runs offline; without it, 20 live Haiku 4.5 calls |
| 3 Tests + CI | `tests/test_offline.py`, `ci.yml` | Copy `ci.yml` to `.github/workflows/ci.yml` in a repo |
| 4 Review + refactor | `13_code_review.py`, `lab4_refactored_client.py` | Refactored version of the file in `sample_diff.patch` |

## Sample data (all fictional)

- `tickets.json`: 20 support tickets for "Nimbus Learning", a made-up course platform.
- `sse_sample.txt`: an illustrative stream in the documented event format.
- `sample_diff.patch`: a deliberately buggy pull request for the review demo. The API key in it is a placeholder.

Models used: `claude-sonnet-5-5`, `claude-opus-5-5` (code review), `claude-haiku-4-5-20251001` (bulk calls).
Facts checked against platform.claude.com and code.claude.com docs, October 2026.

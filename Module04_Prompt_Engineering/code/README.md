# Module 4 · Prompt Engineering · code pack

Claude Certified Developer – Foundations. All company names and data are fictional
(Nimbus Learning is an imaginary online course platform).

## Setup

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install anthropic                                  # SDK 1.x
export ANTHROPIC_API_KEY=sk-ant-...                    # Windows: set ANTHROPIC_API_KEY=...
cd code
```

Run every file from inside `code/` (the harness is imported as a package from there).
Files marked **offline** run without an API key.

## Demos (in teaching order)

| File | Slide | What it shows |
|---|---|---|
| `prompts/classifier_v1.txt` | 9 | The weak first-draft prompt we improve all module |
| `01_clear_direct.py` | 17 | Same task, vague vs clear prompt (what, why, for whom, format) |
| `02_xml_structure.py` | 20 | Context, input and instructions in XML tags; extracting `<summary>` |
| `03_long_context.py` | 22 | Documents first, question last, quotes before the answer (uses `data/`) |
| `04_few_shot.py` | 28 | Five diverse examples inside `<examples>` tags |
| `05_system_vs_user.py` | 34 | Role and rules in `system`; untrusted ticket in the user turn |
| `06_thinking_vs_cot.py` | 40 | Opus 5.5 adaptive thinking + effort vs manual chain of thought on Haiku 4.5 |
| `07_no_prefill.py` | 45 | Replacing prefill: structured outputs and "no preamble" instructions |
| `08_sanitise_input.py` | 50 | **offline** Clean untrusted text and wrap it in random-id `<pasted_content>` tags |
| `harness/registry.py` | 54 | Versioned prompt files -> requests, prompt id = version + hash |
| `09_prompt_registry.py` | 54–55 | **offline** Prints the prompt id and request for v1–v4 |
| `harness/score.py` | 56–57 | **offline** Scores stored outputs against the labelled test set |

## Prompt test harness

```
prompts/classifier_v1.txt .. v4.txt   versioned prompt files (never edit a released one)
prompts/CHANGELOG.md                  what changed in each version, why, and its score
harness/test_set.json                 20 labelled tickets: id, ticket, expected, tags
harness/test_set.csv                  the same 20 cases for spreadsheets (mirror of the JSON)
harness/registry.py                   load_prompt(), clean_ticket(), build_request()
harness/score.py                      exact-match scorer with edge-case and invalid counts
harness/sample_outputs/v1..v4.jsonl   sample outputs, one JSON object per test case
```

```bash
python harness/score.py                      # scores sample_outputs/v1..v4 (offline)
python lab1_iterate_classifier.py v1 v2      # live run -> harness/outputs/, then scores
```

The files in `sample_outputs/` are **illustrative**. They were written by hand to show
the scoring workflow and typical failure patterns, not recorded from a model. Your own
run will give different numbers. That is the point: measure, don't assume.

A prompt file has an optional `=== system ===` section and a `=== user ===` section.
`{{TICKET}}` marks where the cleaned ticket text goes. Lines starting with `#` before
the first section are comments.

## Labs

| File | Lab | Notes |
|---|---|---|
| `lab1_iterate_classifier.py` | 1 · Improve a weak classifier over 4 iterations | Needs a key. ~80 calls on Sonnet 5.5 at effort low |
| `lab2_migrate_prefill.py` | 2 · Migrate a prefill-based extractor to Opus 5.5 | Needs a key |
| `lab3_injection_cases.py` | 3 · Attack and defend the classifier | **offline**; then `TEST_SET=test_set_attacks.json python lab1_iterate_classifier.py v4` |

Model IDs and behaviour (prefill rejected, effort defaults, thinking always on for
Opus 5.5) were checked against platform.claude.com in October 2026. Re-check them
before each cohort.

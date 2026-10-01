# claude-practise

Hands-on practice scripts for the [Claude API](https://platform.claude.com/docs) using the official `anthropic` Python SDK.

Each script is small and self-contained, and focuses on one concept: tokens, cost, conversation growth, sampling, thinking, effort, few-shot prompting or fast mode.

---

## Contents

- [Requirements](#requirements)
- [Setup](#setup)
- [Environment variables](#environment-variables)
- [Running scripts](#running-scripts)
- [Project layout](#project-layout)
- [Module 1: Claude API fundamentals](#module-1-claude-api-fundamentals)
- [Models and pricing](#models-and-pricing)
- [Adding a new module](#adding-a-new-module)

---

## Requirements

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- An Anthropic API key

## Setup

```bash
# 1. Install dependencies
uv sync

# 2. Create your .env file from the template
cp .env.example .env

# 3. Open .env and set ANTHROPIC_API_KEY
```

## Environment variables

The project uses **one `.env` file at the project root**, shared by every script in every module folder.

| Variable            | Required | Used by                                        |
| ------------------- | -------- | ---------------------------------------------- |
| `ANTHROPIC_API_KEY` | Yes      | Every script                                   |
| `CLAUDE_MODEL`      | No       | `sample.py` (defaults to `claude-sonnet-5-5`)  |

**How the scripts find it:** each script calls `load_dotenv()`. It looks for a `.env` file in the script's own folder first, then moves up one folder at a time. Scripts in `Module1_code/` (or any future module folder) therefore find the root `.env` automatically.

**Keep it secret:** `.env` is listed in `.gitignore` and must never be committed. Only `.env.example`, which holds placeholder values, belongs in git.

> Don't put a separate `.env` inside a module folder. `load_dotenv()` stops at the first `.env` it finds, so that module's scripts would stop reading the root file.

## Running scripts

Run commands from the project root:

```bash
uv run main.py                          # list every available script
uv run demo.py                          # first request
uv run Module1_code/lab1_tokens.py      # any module script
```

> **Cost note:** every script except `main.py` and `Module1_code/lab2_cost.py` calls the API and is billed to your key.

## Project layout

```
claude-practise/
├── main.py              # Lists all available scripts
├── demo.py              # Minimal first request
├── sample.py            # System prompt, model from .env, error handling
├── Module1_code/        # Module 1: Claude API fundamentals
│   ├── *.py             #   concept demos
│   └── lab*.py          #   hands-on labs
├── .env                 # Your API key (git-ignored; create from .env.example)
├── .env.example         # Template for .env
├── pyproject.toml       # Project metadata and dependencies
└── uv.lock              # Locked dependency versions
```

### Root scripts

| Script      | What it does                                                                         |
| ----------- | ------------------------------------------------------------------------------------ |
| `main.py`   | Prints the list of practice scripts (no API call)                                    |
| `demo.py`   | Sends one message and prints the text, `stop_reason` and token `usage`              |
| `sample.py` | Adds a system prompt, reads the model from `CLAUDE_MODEL` and handles API errors |

## Module 1: Claude API fundamentals

Module 1 has two kinds of files:

- **Concept demos:** short snippets that introduce one idea.
- **Labs:** longer exercises that build on a demo and measure the results.

### Concept demos

| Script              | What it shows                                                                    | Expanded in        |
| ------------------- | -------------------------------------------------------------------------------- | ------------------ |
| `hello_claude.py`   | Basic `messages.create` call: reading content blocks, `stop_reason` and `usage`  | `demo.py` (root)   |
| `count_tokens.py`   | `messages.count_tokens` for one text across Haiku, Sonnet and Opus               | `lab1_tokens.py`   |
| `cost.py`           | Turning a real response's `usage` into a USD cost                               | `lab2_cost.py`     |
| `chat_growth.py`    | The API is stateless, so the full history is resent and input tokens grow     | `lab3_growth.py`   |
| `sampling.py`       | Output variety at `temperature` 0.0 vs 1.0                                       | `lab4_sampling.py` |
| `thinking.py`       | Adaptive thinking with a summarized thinking display and `output_config.effort` | `lab5_effort.py`   |
| `few_shot.py`       | Sentiment classification with XML-tagged examples                               | `lab6_fewshot.py`  |
| `thinking_haiku.py` | Extended thinking on Haiku 4.5 using `budget_tokens`                             | n/a                |
| `fast_mode.py`      | Opus fast mode (beta `fast-mode-2026-02-01` with `speed="fast"`)                 | n/a                |

### Labs

| Lab                | Exercise                                                                                 | API calls |
| ------------------ | ---------------------------------------------------------------------------------------- | --------- |
| `lab1_tokens.py`   | Compare token counts for English, Hindi, Python and JSON across three models             | Yes       |
| `lab2_cost.py`     | Estimate daily and monthly cost of 5,000 conversations per model                         | **No**    |
| `lab3_growth.py`   | Run a 10-turn trip-planning chat and track how input tokens accumulate                   | Yes       |
| `lab4_sampling.py` | Count unique outputs per temperature and show that Opus 5.5 rejects `temperature`        | Yes       |
| `lab5_effort.py`   | Compare output tokens, latency and cost at `low`, `medium` and `high` effort on a puzzle | Yes       |
| `lab6_fewshot.py`  | Compare zero-shot and few-shot accuracy and token cost on 10 labelled messages           | Yes       |

## Models and pricing

USD per 1 million tokens, as used in `cost.py` and `lab2_cost.py`:

| Model      | Model ID                    | Input | Output |
| ---------- | --------------------------- | ----: | -----: |
| Haiku 4.5  | `claude-haiku-4-5-20251001` |    $1 |     $5 |
| Sonnet 5.5 | `claude-sonnet-5-5`         |    $2 |    $10 |
| Opus 5.5   | `claude-opus-5-5`           |    $4 |    $20 |
| Fable 5.1  | `claude-fable-5-1`          |   $10 |    $50 |

Some scripts rely on behaviour that differs between models:

- **Sampling:** Opus 5.5 and Sonnet 5.5 reject sampling parameters such as `temperature`. `lab4_sampling.py` demonstrates this.
- **Thinking:** Haiku 4.5 sets a fixed thinking budget with `{"type": "enabled", "budget_tokens": N}`. Newer models use `{"type": "adaptive"}` and control depth with `output_config.effort`.
- **Fast mode:** available on Opus only, through the Claude API.

Prices change over time. Check the [pricing page](https://platform.claude.com/docs/en/about-claude/pricing) before relying on these numbers.

## Adding a new module

1. Create a folder next to `Module1_code`, for example `Module2_code/`.
2. Start each script with:

   ```python
   import anthropic
   from dotenv import load_dotenv

   load_dotenv()  # finds the root .env automatically
   client = anthropic.Anthropic()
   ```

3. Don't create a `.env` in the new folder. The root `.env` is shared.
4. Add a section for the module to this README.

`main.py` lists scripts from every folder whose name starts with `Module`, so new modules show up there automatically.

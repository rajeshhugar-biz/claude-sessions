"""Lab 1 solution: run prompt versions on the 20-case test set, store, then score.

Usage:  python lab1_iterate_classifier.py v1 v2 v3 v4    (needs ANTHROPIC_API_KEY)
Writes harness/outputs/<version>.jsonl, then scores them with harness/score.py.
"""
import json
import sys
from pathlib import Path

import anthropic
from harness.registry import build_request, load_prompt
from harness.score import TEST_SET, main as score

HERE = Path(__file__).resolve().parent
OUT_DIR = HERE / "harness" / "outputs"
client = anthropic.Anthropic()
cases = json.loads(TEST_SET.read_text(encoding="utf-8"))


def run(version: str) -> Path:
    prompt = load_prompt(version)
    OUT_DIR.mkdir(exist_ok=True)
    out = OUT_DIR / f"{version}.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for case in cases:
            r = client.messages.create(**build_request(prompt, case["ticket"]))
            text = "".join(b.text for b in r.content if b.type == "text")
            f.write(json.dumps({"id": case["id"], "version": version,
                                "prompt_id": prompt["id"], "model": r.model,
                                "stop_reason": r.stop_reason, "output": text},
                               ensure_ascii=False) + "\n")
    print(f"{prompt['id']}: {len(cases)} outputs -> {out.relative_to(HERE)}")
    return out


if __name__ == "__main__":
    versions = sys.argv[1:] or ["v1", "v2", "v3", "v4"]
    score([str(run(v)) for v in versions])

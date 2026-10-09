"""Score stored classifier outputs against the labelled test set (no API needed).

Usage:  python harness/score.py                   # all files in sample_outputs/
        python harness/score.py harness/outputs/v3.jsonl harness/outputs/v4.jsonl
Set TEST_SET=test_set_attacks.json to score against another file in harness/.
"""
import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LABELS = {"billing", "technical", "account", "content", "other"}
TEST_SET = HERE / os.environ.get("TEST_SET", "test_set.json")


def normalise(output: str) -> str:
    """Return the label in a reply, or INVALID if it is not exactly one label."""
    m = re.search(r"<label>(.*?)</label>", output, re.S | re.I)
    text = (m.group(1) if m else output).strip().strip(".").lower()
    return text if text in LABELS else "INVALID"


def score(cases: dict, path: Path) -> dict:
    rows = [json.loads(ln) for ln in path.read_text(encoding="utf-8").splitlines()
            if ln.strip()]
    r = {"version": path.stem, "n": 0, "correct": 0, "invalid": 0,
         "edge": [0, 0], "fails": []}
    for row in rows:
        case = cases[row["id"]]
        got = normalise(row["output"])
        if row.get("stop_reason") != "end_turn":   # max_tokens, refusal...
            got = "INVALID"
        ok = got == case["expected"]
        r["n"] += 1
        r["correct"] += ok
        r["invalid"] += got == "INVALID"
        if "edge" in case["tags"]:
            r["edge"][0] += ok
            r["edge"][1] += 1
        if not ok:
            r["fails"].append((case["id"], case["expected"], got))
    if r["n"] != len(cases):
        print(f"WARNING {path.name}: {r['n']} outputs for {len(cases)} cases")
    return r


def main(paths):
    text = TEST_SET.read_text(encoding="utf-8")
    cases = {c["id"]: c for c in json.loads(text)}
    default = sorted((HERE / "sample_outputs").glob("*.jsonl"))
    files = [Path(p) for p in paths] or default
    print(f"{'version':9}{'correct':>9}{'acc':>6}{'invalid':>9}{'edge':>7}")
    for path in files:
        r = score(cases, path)
        print(f"{r['version']:9}{r['correct']:>6}/{r['n']:<2}"
              f"{r['correct'] / r['n']:>6.0%}{r['invalid']:>9}"
              f"{r['edge'][0]:>5}/{r['edge'][1]}")
    print(f"\nFailures in {r['version']} (id, expected, got):")
    for fail in r["fails"]:
        print("  ", fail)
    return r


if __name__ == "__main__":
    main(sys.argv[1:])

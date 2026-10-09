# Classifier prompt changelog

Each version is a separate file. Never edit a released version: copy it, change
one thing, give it the next number, and record the change and its score here.
Scores are from `harness/score.py` on the 20-case test set (sample outputs).

| Version | Change | Why | Score |
|---|---|---|---|
| v1 | First draft: "Classify this support ticket" | Baseline | 3/20 (15%) |
| v2 | Role, audience, why; five labels with definitions; label-only output | Replies were free text and could not be parsed | 14/20 (70%) |
| v3 | XML tags; ticket in the user turn as data; rules for multi-issue, injected instructions, empty tickets, Hindi | Edge cases failed; one ticket's instruction was obeyed | 17/20 (85%) |
| v4 | Six examples covering login-email and certificate-name cases | Account tickets still went to technical/content | 19/20 (95%) |

Model pinned for all versions: `claude-sonnet-5-5`, effort `low` (see `harness/registry.py`).
Open issue after v4: case 19 (instructor conduct) - decide whether it is `content`
or `other` and write that into the label definitions in v5.

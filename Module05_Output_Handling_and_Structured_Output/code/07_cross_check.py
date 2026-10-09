"""Offline: a schema-valid, confident extraction that is still wrong."""
import json
from checks import invoice_problems
from invoice_models import Invoice

with open("sample_extraction.json", encoding="utf-8") as f:
    inv = Invoice.model_validate(json.load(f))  # passes: types are all fine
with open("invoice_nimbus.txt", encoding="utf-8") as f:
    source = f.read()

print("Schema check: PASSED. Model's note:", repr(inv.notes))
problems = invoice_problems(inv, source_text=source)
for p in problems:
    print("  PROBLEM:", p)
print("Decision:", "send to human review" if problems else "auto-approve")

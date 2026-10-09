"""Lab starter: fill in the TODOs. The full solution is lab1_invoice_extractor.py.

Goal: invoice_nimbus.txt (or .png) -> a validated Invoice, retried on failure.
Run the offline tests first:  python -m unittest -v
"""
import anthropic
from invoice_models import Invoice  # read it: which fields are nullable? optional?
from safe_json import extract_json  # noqa: F401  (you will need it)

PROMPT = "Extract the invoice fields."  # TODO 1: tighten the instructions


def extract_once(client, invoice_text):
    """TODO 2: one call with output_config={"format": ...} built from Invoice.

    Hint: from anthropic import transform_schema. Check stop_reason first,
    select the text block by type, then Invoice.model_validate(...).
    """
    raise NotImplementedError


def problems(inv):
    """TODO 3: return a list of strings, one per broken business rule.

    Ideas: quantity x unit_price == amount, lines add up to subtotal,
    subtotal + tax_amount == total, due_date not before invoice_date.
    """
    return []


def extract_with_retry(client, invoice_text, max_attempts=3):
    """TODO 4: loop. On a ValidationError or a rule problem, send the problems
    back as a new user turn and try again. Give up after max_attempts."""
    raise NotImplementedError


if __name__ == "__main__":
    with open("invoice_nimbus.txt", encoding="utf-8") as f:
        print(extract_with_retry(anthropic.Anthropic(), f.read()))

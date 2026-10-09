"""Lab solution: invoice (text or PNG) -> validated Invoice JSON with auto-retry.

Usage:  python lab1_invoice_extractor.py invoice_nimbus.txt
        python lab1_invoice_extractor.py invoice_nimbus.png
"""
import base64
import sys
import anthropic
from checks import invoice_problems
from invoice_models import Invoice
from retry_extract import ExtractionError, extract_with_retry

PROMPT = ("Extract the invoice fields. Dates as YYYY-MM-DD. Amounts as plain "
          "numbers exactly as printed, without commas or currency symbols. "
          "Use null for anything that is not printed. Do not calculate or "
          "correct any values.")


def build_content(path):
    """Return (content blocks, source text or None) for a .txt or .png invoice."""
    if path.lower().endswith(".png"):
        with open(path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode("utf-8")
        image = {"type": "image", "source": {
            "type": "base64", "media_type": "image/png", "data": data}}
        return [image, {"type": "text", "text": PROMPT}], None
    with open(path, encoding="utf-8") as f:
        source = f.read()
    text = f"<invoice>\n{source}\n</invoice>\n\n{PROMPT}"
    return [{"type": "text", "text": text}], source


def main(path="invoice_nimbus.txt"):
    client = anthropic.Anthropic()
    content, source = build_content(path)
    try:
        inv, attempts = extract_with_retry(
            client, Invoice, content,
            rules=lambda i: invoice_problems(i, source_text=source))
    except ExtractionError as e:
        print("NEEDS HUMAN REVIEW:", e)
        return 1
    print(f"Valid after {attempts} attempt(s)")
    print(inv.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))

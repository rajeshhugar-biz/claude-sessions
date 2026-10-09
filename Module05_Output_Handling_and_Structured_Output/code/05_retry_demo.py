"""Offline demo of the retry loop: a fake client plays three scripted replies."""
from types import SimpleNamespace as NS
from checks import invoice_problems
from invoice_models import Invoice
from retry_extract import extract_with_retry

GOOD = ('{"invoice_number": "NL-2026-0412", "invoice_date": "2026-09-30", '
        '"due_date": "2026-10-30", "vendor_name": "Nimbus Learning Pvt. Ltd.", '
        '"customer_name": "Acme Retail Pvt. Ltd.", "currency": "INR", '
        '"line_items": [{"description": "Workshop seat", "quantity": 12, '
        '"unit_price": 8500, "amount": 102000}], "subtotal": 102000, '
        '"tax_rate_percent": 18, "tax_amount": 18360, "total": 120360}')
REPLIES = [
    "Sure! Here is the invoice:\n" + GOOD.replace('"INR"', '"Rupees"'),  # bad enum
    "```json\n" + GOOD.replace("120360", "120630") + "\n```",  # wrong total
    GOOD,
]


class FakeMessages:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        text = REPLIES[len(self.calls) - 1]
        print(f"--- attempt {len(self.calls)} gets: {text[:60]!r}...")
        return NS(stop_reason="end_turn", content=[NS(type="text", text=text)])


client = NS(messages=FakeMessages())
inv, attempts = extract_with_retry(client, Invoice, "<invoice text>",
                                   rules=invoice_problems)
print(f"\nvalid after {attempts} attempts: total={inv.total}")
for msg in client.messages.calls[-1]["messages"][1:]:
    if msg["role"] == "user":
        print("feedback sent:", msg["content"].splitlines()[1][:70])

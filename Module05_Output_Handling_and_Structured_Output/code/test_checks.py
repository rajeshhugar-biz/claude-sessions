"""Tests for the business-rule checks. Run: python -m unittest -v"""
import json
import unittest
from checks import appears_in, invoice_problems
from invoice_models import Invoice

with open("invoice_nimbus.txt", encoding="utf-8") as f:
    SOURCE = f.read()
with open("sample_extraction.json", encoding="utf-8") as f:
    WRONG = json.load(f)

CORRECT = dict(WRONG, total=135582.0, notes=None, line_items=[
    dict(WRONG["line_items"][0]), dict(WRONG["line_items"][1]),
    dict(WRONG["line_items"][2], amount=7500.0)])


class CheckTests(unittest.TestCase):
    def test_correct_invoice_has_no_problems(self):
        inv = Invoice.model_validate(CORRECT)
        self.assertEqual(invoice_problems(inv, source_text=SOURCE), [])

    def test_sample_extraction_is_caught(self):
        problems = invoice_problems(Invoice.model_validate(WRONG), source_text=SOURCE)
        text = "\n".join(problems)
        self.assertIn("line 3", text)
        self.assertIn("add up to", text)
        self.assertIn("not 135852.0", text)
        self.assertIn("total 135852.0 is not printed", text)

    def test_wrong_tax(self):
        inv = Invoice.model_validate(dict(CORRECT, tax_amount=20000.0))
        self.assertTrue(any("tax should be" in p for p in invoice_problems(inv)))

    def test_due_date_before_invoice_date(self):
        inv = Invoice.model_validate(dict(CORRECT, due_date="2026-09-01"))
        self.assertIn("due_date is before invoice_date", invoice_problems(inv))

    def test_appears_in_handles_indian_grouping(self):
        self.assertTrue(appears_in(135582.0, "TOTAL 1,35,582.00"))
        self.assertFalse(appears_in(135852.0, "TOTAL 1,35,582.00"))

    def test_schema_rejects_bad_types(self):
        with self.assertRaises(ValueError):
            Invoice.model_validate(dict(CORRECT, invoice_date="30 September"))
        with self.assertRaises(ValueError):
            Invoice.model_validate(dict(CORRECT, line_items=[]))


if __name__ == "__main__":
    unittest.main()

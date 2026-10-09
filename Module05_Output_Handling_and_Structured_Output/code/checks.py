"""Business-rule checks: recompute numbers instead of trusting confident output."""
import re

TOL = 0.01  # money tolerance (one paisa / one cent)


def appears_in(value, text):
    """True if the number is printed somewhere in the source (commas ignored)."""
    found = re.findall(r"\d+(?:\.\d+)?", text.replace(",", ""))
    return any(abs(float(n) - value) <= TOL for n in found)


def invoice_problems(inv, source_text=None):
    problems = []
    for i, li in enumerate(inv.line_items, 1):
        if abs(li.quantity * li.unit_price - li.amount) > TOL:
            problems.append(f"line {i}: {li.quantity} x {li.unit_price} != {li.amount}")
    lines_sum = round(sum(li.amount for li in inv.line_items), 2)
    if abs(lines_sum - inv.subtotal) > TOL:
        problems.append(f"line amounts add up to {lines_sum}, not {inv.subtotal}")
    if inv.tax_rate_percent is not None:
        tax = round(inv.subtotal * inv.tax_rate_percent / 100, 2)
        if abs(tax - inv.tax_amount) > TOL:
            problems.append(f"tax should be {tax}, not {inv.tax_amount}")
    if abs(inv.subtotal + inv.tax_amount - inv.total) > TOL:
        problems.append(f"subtotal + tax = {inv.subtotal + inv.tax_amount:.2f}, "
                        f"not {inv.total}")
    if inv.due_date and inv.due_date < inv.invoice_date:
        problems.append("due_date is before invoice_date")
    for field in ("subtotal", "tax_amount", "total") if source_text else ():
        value = getattr(inv, field)
        if not appears_in(value, source_text):
            problems.append(f"{field} {value} is not printed on the invoice")
    return problems

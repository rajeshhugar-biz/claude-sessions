"""Generate the fictional sample invoice as invoice_nimbus.txt and invoice_nimbus.png.

Run once: python make_invoice.py   (needs Pillow: pip install pillow)
"""
from PIL import Image, ImageDraw, ImageFont

ITEMS = [  # description, quantity, unit price (INR)
    ("Claude Developer Foundations workshop (per seat)", 12, 8500.00),
    ("Course workbook, printed", 12, 450.00),
    ("Lab environment setup (one-time)", 1, 7500.00),
]
GST_RATE = 18


def inr(x):
    """Indian digit grouping: 135582.0 -> '1,35,582.00'."""
    whole, frac = f"{x:.2f}".split(".")
    head, tail = whole[:-3], whole[-3:]
    groups = []
    while len(head) > 2:
        groups.insert(0, head[-2:])
        head = head[:-2]
    if head:
        groups.insert(0, head)
    return ",".join(groups + [tail]) + "." + frac


def invoice_lines():
    subtotal = sum(q * p for _, q, p in ITEMS)
    tax = round(subtotal * GST_RATE / 100, 2)
    rows = [
        "NIMBUS LEARNING PVT. LTD.",
        "Office 4, Riverside Business Park, Pune 411001",
        "",
        "TAX INVOICE",
        "Invoice No: NL-2026-0412        Invoice Date: 30-Sep-2026",
        "Payment due: 30-Oct-2026        Currency: INR",
        "",
        "Bill to: Acme Retail Pvt. Ltd., Hyderabad",
        "",
        f"{'#':<3}{'Description':<52}{'Qty':>5}{'Rate':>12}{'Amount':>14}",
    ]
    for i, (d, q, p) in enumerate(ITEMS, 1):
        rows.append(f"{i:<3}{d:<52}{q:>5}{inr(p):>12}{inr(q * p):>14}")
    rows += [
        "",
        f"{'Subtotal':>72}{inr(subtotal):>14}",
        f"{'GST @ ' + str(GST_RATE) + '%':>72}{inr(tax):>14}",
        f"{'TOTAL (INR)':>72}{inr(subtotal + tax):>14}",
        "",
        "Bank transfer within 30 days. Thank you for training with Nimbus Learning.",
    ]
    return rows


def font(size):
    for name in ("DejaVuSansMono.ttf", "consola.ttf", "Menlo.ttc", "cour.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def main():
    rows = invoice_lines()
    with open("invoice_nimbus.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(rows) + "\n")
    fnt, big = font(18), font(26)
    img = Image.new("RGB", (1100, 40 + 30 * len(rows) + 40), "white")
    draw = ImageDraw.Draw(img)
    y = 40
    for i, row in enumerate(rows):
        draw.text((40, y), row, fill=(20, 30, 60), font=big if i == 0 else fnt)
        y += 38 if i == 0 else 30
    draw.rectangle((20, 20, img.width - 20, img.height - 20), outline=(31, 42, 68))
    img.save("invoice_nimbus.png")
    print("wrote invoice_nimbus.txt and invoice_nimbus.png", img.size)


if __name__ == "__main__":
    main()

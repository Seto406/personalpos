import re
from app.schemas import ReceiptAnalyzeOut, ParsedReceiptItem


LINE_PATTERN = re.compile(
    r"(?P<desc>[A-Za-z0-9\s\-\.]+)\s+x(?P<qty>[0-9]+(?:\.[0-9]+)?)\s+@\s+(?P<unit>[0-9]+(?:\.[0-9]+)?)"
)


def analyze_receipt_text(ocr_text: str) -> ReceiptAnalyzeOut:
    """
    MVP parser for OCR text.

    Expected line format example:
    "Coke 330ml x2 @ 15"
    "Bread x1 @ 30"
    """
    items = []
    warnings = []

    supplier = None
    for raw_line in ocr_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.lower().startswith("supplier:"):
            supplier = line.split(":", 1)[1].strip() or None
            continue

        m = LINE_PATTERN.search(line)
        if not m:
            continue

        desc = m.group("desc").strip()
        qty = float(m.group("qty"))
        unit = float(m.group("unit"))
        items.append(
            ParsedReceiptItem(
                description=desc,
                quantity=qty,
                unit_price=unit,
                line_total=round(qty * unit, 2),
            )
        )

    if not items:
        warnings.append("No line items matched expected pattern: '<name> x<qty> @ <unit_price>'")

    subtotal = round(sum(i.line_total for i in items), 2)
    estimated_tax = round(subtotal * 0.12, 2) if subtotal else 0.0
    grand_total = round(subtotal + estimated_tax, 2)
    confidence = 0.85 if items else 0.3

    return ReceiptAnalyzeOut(
        supplier_name=supplier,
        items=items,
        subtotal=subtotal,
        estimated_tax=estimated_tax,
        grand_total=grand_total,
        confidence=confidence,
        warnings=warnings,
    )

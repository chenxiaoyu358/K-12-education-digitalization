"""Chinese currency amount parsing — all values normalized to CNY (元)."""

import re
from decimal import Decimal, InvalidOperation
from typing import Optional

# Patterns: "123.45万元", "1,234.56元", "0.5亿元", "123.45（万元）"
_AMOUNT_PATTERN = re.compile(
    r"([\d,]+\.?\d*)\s*(?:[（(]?\s*(万|亿)\s*[）)]?\s*)?元?"
)


def parse_amount(raw: str) -> Optional[Decimal]:
    """Parse a Chinese currency string to Decimal in 元 (CNY).

    Examples:
        "123.45万元" -> Decimal("1234500")
        "1,234.56元" -> Decimal("1234.56")
        "0.5亿元"    -> Decimal("50000000")
        "50000"      -> Decimal("50000")
    """
    if not raw:
        return None
    raw = raw.strip().replace(",", "").replace("，", "")
    match = _AMOUNT_PATTERN.search(raw)
    if not match:
        # Try plain number
        try:
            return Decimal(re.sub(r"[^\d.]", "", raw))
        except (InvalidOperation, ValueError):
            return None
    number_str = match.group(1).replace(",", "")
    unit = match.group(2)
    try:
        value = Decimal(number_str)
    except (InvalidOperation, ValueError):
        return None
    if unit == "万":
        value *= 10000
    elif unit == "亿":
        value *= 100000000
    return value

"""Chinese date parsing utilities."""

import re
from datetime import date, datetime
from typing import Optional


# Common Chinese date patterns
_PATTERNS = [
    # 2024年03月15日
    (re.compile(r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日"), "%Y-%m-%d"),
    # 2024-03-15, 2024/03/15
    (re.compile(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})"), "%Y-%m-%d"),
    # 2024.03.15
    (re.compile(r"(\d{4})\.(\d{1,2})\.(\d{1,2})"), "%Y-%m-%d"),
]


def parse_date(raw: str) -> Optional[date]:
    """Parse Chinese date string to date object.

    Supported formats:
        "2024年03月15日" -> date(2024, 3, 15)
        "2024-03-15"     -> date(2024, 3, 15)
        "2024/3/15"      -> date(2024, 3, 15)
        "2024.03.15"     -> date(2024, 3, 15)
    """
    if not raw:
        return None
    raw = raw.strip()
    for pattern, _ in _PATTERNS:
        match = pattern.search(raw)
        if match:
            try:
                year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                return date(year, month, day)
            except ValueError:
                continue
    # Fallback: try dateutil
    try:
        from dateutil.parser import parse as du_parse
        return du_parse(raw).date()
    except (ValueError, ImportError):
        return None


def parse_datetime(raw: str) -> Optional[datetime]:
    """Parse Chinese datetime string."""
    if not raw:
        return None
    d = parse_date(raw)
    if d is None:
        return None
    # Try to extract time part
    time_match = re.search(r"(\d{1,2}):(\d{2})(?::(\d{2}))?", raw)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2))
        second = int(time_match.group(3) or 0)
        return datetime(d.year, d.month, d.day, hour, minute, second)
    return datetime(d.year, d.month, d.day)

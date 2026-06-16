"""Chinese text processing utilities."""

import re

from w3lib.html import remove_tags


def clean_html(html: str) -> str:
    """Strip HTML tags and normalize whitespace."""
    text = remove_tags(html)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_whitespace(text: str) -> str:
    """Collapse all whitespace to single spaces."""
    return re.sub(r"\s+", " ", text).strip()

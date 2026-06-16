"""Deduplication hash utilities."""

import hashlib
import re


def compute_dedup_hash(title: str, procurement_unit: str, budget: str, publish_date: str) -> str:
    """Compute SHA256 hash for deduplication.

    Normalizes inputs before hashing to catch near-duplicates:
    - Strip whitespace
    - Remove punctuation
    - Lowercase
    """
    parts = []
    for field in [title, procurement_unit, budget, publish_date]:
        normalized = re.sub(r"[\s\u3000]+", "", str(field or ""))
        normalized = re.sub(r"[，。、；：\u201c\u201d\u2018\u2019【】（）《》\-—_.,;:\"'()\[\]{}]", "", normalized)
        parts.append(normalized.lower())
    raw = "|".join(parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

"""Standalone SHA-256 deduplicator.

The production pipeline collapses cross-source mirror notices with a Redis-backed Scrapy
stage; this is the equivalent dependency-free helper for reuse on any record iterable. It
wraps ``compute_dedup_hash`` (the same normalization used to build the deposited
``dedup_hash`` column) and tracks seen digests in an in-memory set.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Any, Callable

from ztb.utils.hash import compute_dedup_hash


class Deduplicator:
    """Collapse exact cross-source mirror duplicates by content hash.

    >>> d = Deduplicator()
    >>> d.is_duplicate("智慧黑板采购", "某中学", "100000", "2024-05-01")
    False
    >>> d.is_duplicate("智慧黑板采购", "某中学", "100000", "2024-05-01")
    True
    """

    def __init__(self) -> None:
        self._seen: set[str] = set()
        self.checked = 0
        self.duplicates = 0

    def is_duplicate(self, title: str, procurement_unit: str, budget: str,
                     publish_date: str) -> bool:
        """Return True if this (normalized) record was already seen."""
        digest = compute_dedup_hash(title, procurement_unit, budget, publish_date)
        self.checked += 1
        if digest in self._seen:
            self.duplicates += 1
            return True
        self._seen.add(digest)
        return False


def deduplicate(
    records: Iterable[dict[str, Any]],
    *,
    title_key: str = "title",
    unit_key: str = "procurement_unit",
    budget_key: str = "budget_amount",
    date_key: str = "publish_date",
    keep: Callable[[dict, dict], dict] | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield records with exact cross-source mirrors removed (first occurrence kept).

    ``keep`` is reserved for future merge policies; the default keeps the first row.
    """
    d = Deduplicator()
    for rec in records:
        if not d.is_duplicate(
            str(rec.get(title_key, "")),
            str(rec.get(unit_key, "")),
            str(rec.get(budget_key, "")),
            str(rec.get(date_key, "")),
        ):
            yield rec

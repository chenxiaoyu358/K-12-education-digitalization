"""Rule-based project category classifier using jieba + keyword matching."""

from functools import lru_cache

import jieba

from ztb.classification.keywords import load_all_keyword_dicts, load_keywords
from ztb.classification.non_ict_rules import matches_non_ict_pattern
from ztb.constants import Category


@lru_cache(maxsize=1)
def _get_keyword_sets() -> dict[str, set[str]]:
    """Load 8 ICT keyword dictionaries and register with jieba."""
    dicts = load_all_keyword_dicts()
    result = {}
    for cat, keywords in dicts.items():
        for kw in keywords:
            jieba.add_word(kw, freq=1000)
        result[cat] = set(keywords)
    return result


@lru_cache(maxsize=1)
def _get_non_ict_keywords() -> set[str]:
    """Load non_ict fallback dictionary (food/logistics/printing/tours/etc)."""
    keywords = load_keywords("non_ict.txt")
    for kw in keywords:
        jieba.add_word(kw, freq=1000)
    return set(keywords)


def _score_against(
    keywords: set[str],
    title: str,
    title_words: set[str],
    content: str,
    content_words: set[str],
) -> int:
    title_hits = len(title_words & keywords)
    title_substr_hits = sum(1 for kw in keywords if kw in title)
    content_hits = len(content_words & keywords)
    content_substr_hits = sum(1 for kw in keywords if kw in content)
    return (title_hits + title_substr_hits) * 3 + (content_hits + content_substr_hits)


def classify(title: str, content: str = "") -> Category:
    """Classify a procurement project with layered scoring.

    Priority order:
      0. If title matches a high-specificity non-ICT pattern (see
         non_ict_rules.matches_non_ict_pattern), short-circuit to NON_ICT.
      1. Score against 8 ICT category dictionaries; if any score > 0, return the top one.
      2. Otherwise score against `non_ict.txt`; if any match, return NON_ICT.
      3. Otherwise return OTHER (ICT-related but unidentified).

    Rationale: the 720-sample study (docs/analysis/other_category_diagnosis_2026-04-21.md)
    showed 82% of `other` were truly non-ICT noise (食堂/物业/印刷/研学). Treating
    non-ICT as a sibling bucket keeps OTHER reserved for genuine edge cases.
    Round 2 added pattern rules for signals that don't fit a flat dictionary —
    e.g. "竞价采购 + N件" consistently indicates small-daily-goods purchases.

    Args:
        title: Project title (required).
        content: Optional full text content for better accuracy.

    Returns:
        Category enum value.
    """
    if matches_non_ict_pattern(title):
        return Category.NON_ICT

    ict_sets = _get_keyword_sets()
    content_snippet = content[:2000] if content else ""

    title_words = set(jieba.cut(title))
    content_words = set(jieba.cut(content_snippet)) if content_snippet else set()

    ict_scores = {
        cat: _score_against(kws, title, title_words, content_snippet, content_words)
        for cat, kws in ict_sets.items()
    }

    if ict_scores and max(ict_scores.values()) > 0:
        best_cat = max(ict_scores, key=lambda k: ict_scores[k])
        return Category(best_cat)

    non_ict_keywords = _get_non_ict_keywords()
    if non_ict_keywords:
        non_ict_score = _score_against(
            non_ict_keywords, title, title_words, content_snippet, content_words
        )
        if non_ict_score > 0:
            return Category.NON_ICT

    return Category.OTHER

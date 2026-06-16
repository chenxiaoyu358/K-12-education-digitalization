"""Classify the procurement entity (采购主体) by type.

Unlike the project-category classifier (category.py — what is being bought),
this classifier answers: **who is buying**. The procurement_unit field is
short (≤30 chars) and structured — the entity type is almost always encoded
in the suffix word (…教育局, …大学, …小学). So we use priority-ordered
substring rules rather than jieba + keyword scoring.
"""

from __future__ import annotations

from typing import Optional

from ztb.constants import UnitType

# ---------------------------------------------------------------------------
# Keyword lists — ordered within each bucket from most to least specific.
# Scan order across buckets matters: vocational before university before middle
# school so that e.g. "XX职业中学" → vocational, not middle_school.
# ---------------------------------------------------------------------------

_KINDERGARTEN_KEYWORDS = ("幼儿园",)

_VOCATIONAL_KEYWORDS = (
    "职业技术大学",
    "职业技术学院",
    "职业大学",
    "职业学院",
    "职业技术学校",
    "职业学校",
    "职业中学",
    "职业中专",
    "职业教育中心",
    "中等职业学校",
    "中等专业学校",
    "高等专科学校",
    "专科学校",
    "技师学院",
    "技师培训",
    "技工学校",
    "技师",
    "中专",
    "职校",
    "职教中心",
    # Domain-specific trade schools — almost always vocational/secondary
    "卫生学校",
    "工业学校",
    "化工学校",
    "理工学校",
    "经贸学校",
    "艺术学校",
    "铁路学校",
    "农业学校",
    "商贸学校",
    "财经学校",
    "旅游学校",
)

# Applied after vocational, so vocational colleges don't match here.
_UNIVERSITY_KEYWORDS = (
    "大学",
    "学院",
)

_MIDDLE_SCHOOL_KEYWORDS = (
    "高级中学",
    "初级中学",
    "完全中学",
    "九年一贯制学校",
    "实验中学",
    "中学",
)

_ELEMENTARY_KEYWORDS = (
    "实验小学",
    "附属小学",
    "中心小学",
    "中心学校",   # 乡镇中心学校 — typically rural primary
    "中心校",
    "小学",
    "实验学校",   # often grades 1-9, skewed toward primary
    "育才学校",
    "特殊教育学校",
)

# Education authority: 教育局 + subordinate service centers.
_AUTHORITY_KEYWORDS = (
    "教育和体育局",
    "教育科技体育局",
    "教育体育局",
    "教育体育和科学技术局",
    "教育体育和科技局",
    "教育科学技术局",
    "教育局",
    "教育装备管理中心",
    "教育装备",
    "电化教育馆",
    "电化教育站",
    "电化教育",
    "教育信息化管理中心",
    "教育信息化发展中心",
    "教育信息化",
    "教育技术装备",
    "教育技术中心",
    "教育发展中心",
    "教育科学研究院",
    "教研中心",
    "教研室",
    "教育教学研究",
)


_AUTHORITY_ORG_MARKERS = (
    "局", "厅", "委员会", "中心", "馆", "站", "研究所", "研究院",
    "管理办", "办公室", "服务中心", "保障中心",
)

_NON_AUTHORITY_MARKERS = (
    "学校", "学院", "大学", "中学", "小学", "幼儿园", "有限公司",
)


def _is_likely_edu_authority(text: str) -> bool:
    """Fallback: text mentions 教育 AND a gov-office marker, and doesn't look
    like a school or company."""
    if "教育" not in text:
        return False
    if not any(m in text for m in _AUTHORITY_ORG_MARKERS):
        return False
    if any(m in text for m in _NON_AUTHORITY_MARKERS):
        return False
    return True


def _match_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(kw in text for kw in keywords)


def _classify_from_pu(text: str) -> Optional[UnitType]:
    """Priority rules for procurement_unit text.

    Order: kindergarten > vocational > university > middle > elementary >
    authority. `procurement_unit` is short and structured so the entity type
    is usually encoded in the suffix; kindergarten runs first because other
    keywords (学校) can accidentally match it otherwise.
    """
    if _match_any(text, _KINDERGARTEN_KEYWORDS):
        return UnitType.KINDERGARTEN
    if _match_any(text, _VOCATIONAL_KEYWORDS):
        return UnitType.VOCATIONAL
    if _match_any(text, _UNIVERSITY_KEYWORDS):
        return UnitType.UNIVERSITY
    if _match_any(text, _MIDDLE_SCHOOL_KEYWORDS):
        return UnitType.MIDDLE_SCHOOL
    if _match_any(text, _ELEMENTARY_KEYWORDS):
        return UnitType.ELEMENTARY_SCHOOL
    if _match_any(text, _AUTHORITY_KEYWORDS) or _is_likely_edu_authority(text):
        return UnitType.EDUCATION_AUTHORITY
    return None


def _classify_from_title(text: str) -> Optional[UnitType]:
    """Priority rules for title text (used when procurement_unit is empty).

    Titles often contain multiple school-related keywords — the buyer is
    typically named first (e.g., "张北县教育局各学校幼儿园..."), so we check
    education_authority and vocational BEFORE school levels. Kindergarten
    is last because "幼儿园" in a title usually refers to the beneficiary,
    not the buyer.
    """
    if _match_any(text, _AUTHORITY_KEYWORDS) or _is_likely_edu_authority(text):
        return UnitType.EDUCATION_AUTHORITY
    if _match_any(text, _VOCATIONAL_KEYWORDS):
        return UnitType.VOCATIONAL
    if _match_any(text, _UNIVERSITY_KEYWORDS):
        return UnitType.UNIVERSITY
    if _match_any(text, _MIDDLE_SCHOOL_KEYWORDS):
        return UnitType.MIDDLE_SCHOOL
    if _match_any(text, _ELEMENTARY_KEYWORDS):
        return UnitType.ELEMENTARY_SCHOOL
    if _match_any(text, _KINDERGARTEN_KEYWORDS):
        return UnitType.KINDERGARTEN
    return None


# school_type values come from the `schools.school_type` column, populated
# during seeding or by school_resolver. Map them to our UnitType enum.
_SCHOOL_TYPE_MAP: dict[str, UnitType] = {
    "小学": UnitType.ELEMENTARY_SCHOOL,
    "中心校": UnitType.ELEMENTARY_SCHOOL,
    "初中": UnitType.MIDDLE_SCHOOL,
    "初级中学": UnitType.MIDDLE_SCHOOL,
    "高中": UnitType.MIDDLE_SCHOOL,
    "高级中学": UnitType.MIDDLE_SCHOOL,
    "完全中学": UnitType.MIDDLE_SCHOOL,
    "九年一贯制": UnitType.MIDDLE_SCHOOL,
    "中学": UnitType.MIDDLE_SCHOOL,
    "大学": UnitType.UNIVERSITY,
    "学院": UnitType.UNIVERSITY,
    "职业学院": UnitType.VOCATIONAL,
    "职业学校": UnitType.VOCATIONAL,
    "职校": UnitType.VOCATIONAL,
    "技师学院": UnitType.VOCATIONAL,
    "技工学校": UnitType.VOCATIONAL,
    "幼儿园": UnitType.KINDERGARTEN,
}


def classify_unit_type(
    procurement_unit: Optional[str],
    title: Optional[str] = None,
    school_type: Optional[str] = None,
) -> UnitType:
    """Classify the procurement entity type.

    Priority:
      1. ``school_type`` (from ProcurementProject.school_id → School.school_type)
         — authoritative, already resolved against seeded school registry.
      2. ``procurement_unit`` — substring rules (most common path).
      3. ``title`` fallback — useful when procurement_unit is empty; titles
         often contain "XX教育局" or "XX中学" as the project subject.
      4. ``UnitType.OTHER``.
    """
    if school_type:
        mapped = _SCHOOL_TYPE_MAP.get(school_type)
        if mapped is not None:
            return mapped

    if procurement_unit:
        result = _classify_from_pu(procurement_unit)
        if result is not None:
            return result

    if title:
        result = _classify_from_title(title)
        if result is not None:
            return result

    return UnitType.OTHER

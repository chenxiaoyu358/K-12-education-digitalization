"""Geographic entity extraction from procurement text."""

import re
from dataclasses import dataclass
from typing import Iterable, Optional


@dataclass(frozen=True)
class GeoMatch:
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    school: Optional[str] = None


# Province short names -> full names
PROVINCE_SHORT_MAP = {
    "京": "北京", "津": "天津", "沪": "上海", "渝": "重庆",
    "冀": "河北", "豫": "河南", "云": "云南", "辽": "辽宁",
    "黑": "黑龙江", "湘": "湖南", "皖": "安徽", "鲁": "山东",
    "新": "新疆", "苏": "江苏", "浙": "浙江", "赣": "江西",
    "鄂": "湖北", "桂": "广西", "甘": "甘肃", "晋": "山西",
    "蒙": "内蒙古", "陕": "陕西", "吉": "吉林", "闽": "福建",
    "贵": "贵州", "粤": "广东", "川": "四川", "青": "青海",
    "藏": "西藏", "琼": "海南", "宁": "宁夏",
}

# 直辖市 names — these are both province and city level
_MUNICIPALITIES = {"北京", "天津", "上海", "重庆"}

# Common patterns for extracting geography from procurement unit names
_PATTERNS = [
    # Province (省/自治区) + City + District: "广东省深圳市南山区教育局"
    re.compile(
        r"(?P<province>[\u4e00-\u9fa5]{2,8}?(?:省|自治区))"
        r"(?P<city>[\u4e00-\u9fa5]{2,6}?(?:市|地区|自治州|州|盟))"
        r"(?P<district>[\u4e00-\u9fa5]{2,6}?(?:区|县|旗))?"
    ),
    # Province (省/自治区) + City only: "河北省石家庄市教育局"
    re.compile(
        r"(?P<province>[\u4e00-\u9fa5]{2,8}?(?:省|自治区))"
        r"(?P<city>[\u4e00-\u9fa5]{2,6}?(?:市|地区|自治州|州|盟))?"
    ),
    # 直辖市: "北京市海淀区" "上海市浦东新区"
    re.compile(
        r"(?P<province>(?:北京|天津|上海|重庆)市)"
        r"(?P<district>[\u4e00-\u9fa5]{2,6}?(?:区|县))?"
    ),
    # City + District (no province): "南京市鼓楼区"
    re.compile(
        r"(?P<city>[\u4e00-\u9fa5]{2,6}?市)"
        r"(?P<district>[\u4e00-\u9fa5]{2,6}?(?:区|县|旗))?"
    ),
    # District only: "海淀区" "光山县"
    re.compile(
        r"(?P<district>[\u4e00-\u9fa5]{2,6}?(?:区|县|旗))"
    ),
]

# School name patterns
_SCHOOL_PATTERN = re.compile(
    r"([\u4e00-\u9fa5]+(?:小学|中学|高中|初中|学校|中心校|实验学校|附属学校|外国语学校))"
)


def extract_geography(text: str) -> GeoMatch:
    """Extract geographic entities from text (typically procurement_unit or title).

    Returns a GeoMatch with whatever entities could be extracted.
    """
    province = None
    city = None
    district = None
    school = None

    for pattern in _PATTERNS:
        match = pattern.search(text)
        if match:
            groups = match.groupdict()
            if not province and groups.get("province"):
                province = groups["province"]
            if not city and groups.get("city"):
                city = groups["city"]
            if not district and groups.get("district"):
                district = groups["district"]
            if province or city or district:
                break

    # Try to find school name
    school_match = _SCHOOL_PATTERN.search(text)
    if school_match:
        school = school_match.group(1)

    return GeoMatch(province=province, city=city, district=district, school=school)


# Caigou content_text stores a structured admin region field, e.g.
#   "... 行政区域山东 济宁 公告时间 ..."
#   "... 行政区域内蒙古 本网 ..."
#   "... 行政区域山西 运城 稷山县 本网 ..."
_CAIGOU_ADMIN_RE = re.compile(
    r"行政区域\s*"
    r"(?P<a>[\u4e00-\u9fa5]{2,8})"
    r"(?:\s+(?P<b>[\u4e00-\u9fa5]{2,6}))?"
    r"(?:\s+(?P<c>[\u4e00-\u9fa5]{2,6}))?"
)

# Stop-token prefixes — any captured token beginning with one of these is a
# downstream section header that leaked into the greedy capture.
_CAIGOU_STOP_PREFIXES = (
    "公告",
    "本网",
    "本公",
    "预算",
    "行政",
    "所属",
    "采购",
    "品目",
    "中标",
    "招标",
    "结果",
    "预选",
    "项目",
)


def _is_caigou_stop_token(token: Optional[str]) -> bool:
    if not token:
        return True
    return any(token.startswith(p) for p in _CAIGOU_STOP_PREFIXES)


def extract_admin_region_from_caigou_content(content_text: str) -> Optional[GeoMatch]:
    """Extract (province, city, district) from caigou source's "行政区域" field.

    Returns None if the field is not present. Tokens whose prefix matches
    _CAIGOU_STOP_PREFIXES are dropped (downstream section headers that leaked
    into the greedy capture).
    """
    if not content_text:
        return None
    m = _CAIGOU_ADMIN_RE.search(content_text)
    if not m:
        return None
    tokens = [m.group("a"), m.group("b"), m.group("c")]
    cleaned: list[str] = []
    for t in tokens:
        if _is_caigou_stop_token(t):
            break  # stop once we hit a section-header token
        cleaned.append(t)
    if not cleaned:
        return None
    province = cleaned[0] if len(cleaned) >= 1 else None
    city = cleaned[1] if len(cleaned) >= 2 else None
    district = cleaned[2] if len(cleaned) >= 3 else None
    return GeoMatch(province=province, city=city, district=district)


def extract_geography_from_texts(texts: Iterable[str]) -> GeoMatch:
    """Run extract_geography over a sequence of texts, returning the richest match.

    Stops early once province + city have been found.
    """
    best = GeoMatch()
    for text in texts:
        if not text:
            continue
        geo = extract_geography(text)
        best = GeoMatch(
            province=best.province or geo.province,
            city=best.city or geo.city,
            district=best.district or geo.district,
            school=best.school or geo.school,
        )
        if best.province and best.city:
            break
    return best


# Well-known institutions whose names lack an admin-suffix and therefore
# cannot be geocoded via regex. Maps keyword found in text -> (province, city).
# Values match the canonical DB names (stripped of 省/市 suffix where possible;
# the repository.find_*_by_name() helpers handle both exact and contains lookup).
INSTITUTION_LOCATION_MAP: dict[str, tuple[str, str]] = {
    # 四川
    "四川农业大学": ("四川", "雅安"),
    "成都医学院": ("四川", "成都"),
    "中北大学": ("山西", "太原"),
    # 云南
    "云南师范大学": ("云南", "昆明"),
    "云南大学": ("云南", "昆明"),
    # 辽宁 / 大连
    "大连海洋大学": ("辽宁", "大连"),
    "大连外国语大学": ("辽宁", "大连"),
    "辽宁师范大学": ("辽宁", "大连"),
    # 山东
    "鲁中职业学院": ("山东", "淄博"),
    "枣庄学院": ("山东", "枣庄"),
    # 广东
    "广东交通职业技术学院": ("广东", "广州"),
    "华南理工大学": ("广东", "广州"),
    "岭南师范学院": ("广东", "湛江"),
    "深圳技师学院": ("广东", "深圳"),
    # 福建
    "闽南师范大学": ("福建", "漳州"),
    "湄洲湾职业技术学院": ("福建", "莆田"),
    "厦门医学院": ("福建", "厦门"),
    "福建技术师范学院": ("福建", "福州"),
    # 安徽
    "蚌埠学院": ("安徽", "蚌埠"),
    "皖南医学院": ("安徽", "芜湖"),
    "安徽医科大学": ("安徽", "合肥"),
    # 江西
    "江西应用技术职业学院": ("江西", "赣州"),
    # 河北
    "冀中职业学院": ("河北", "沧州"),
    # 陕西
    "延安职业技术学院": ("陕西", "延安"),
    # 吉林
    "长春中医药大学": ("吉林", "长春"),
    # 黑龙江
    "哈尔滨职业技术学院": ("黑龙江", "哈尔滨"),
    # 湖北
    "汉江师范学院": ("湖北", "十堰"),
    # 湖南
    "岳阳职业技术学院": ("湖南", "岳阳"),
    # 内蒙古
    "内蒙古科技大学包头师范学院": ("内蒙古", "包头"),
    # 重庆
    "重庆三峡学院": ("重庆", "重庆"),
    "重庆电子工程职业学院": ("重庆", "重庆"),
}


def match_institution(text: str) -> Optional[tuple[str, str]]:
    """Return (province, city) if text contains a known institution keyword."""
    if not text:
        return None
    # Longest-keyword wins to avoid "云南大学" matching before "云南师范大学".
    for key in sorted(INSTITUTION_LOCATION_MAP, key=len, reverse=True):
        if key in text:
            return INSTITUTION_LOCATION_MAP[key]
    return None

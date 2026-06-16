"""Tests for the file-backed geocoder and the standalone deduplicator."""

from ztb.classification.geocode import Geocoder
from ztb.classification.geography import extract_geography
from ztb.utils.dedup import Deduplicator, deduplicate


def test_extract_geography_full_chain():
    g = extract_geography("广东省深圳市南山区南山小学")
    assert g.province == "广东省"
    assert g.city == "深圳市"
    assert g.district == "南山区"


def test_geocode_province_city_district():
    gc = Geocoder()
    r = gc.geocode("广东省深圳市南山区教育局")
    assert r.province_code == "440000"
    assert r.city_code == "440300"
    assert r.district_code == "440305"
    assert r.resolution_level == "district"


def test_geocode_municipality_district():
    gc = Geocoder()
    r = gc.geocode("北京市海淀区中关村第二小学")
    assert r.province_code == "110000"
    assert r.district_name == "海淀区"
    assert r.resolution_level == "district"


def test_geocode_unresolved():
    gc = Geocoder()
    r = gc.geocode("某不存在的地方采购")
    assert r.resolution_level == "unresolved"


def test_deduplicator_collapses_exact_mirror():
    d = Deduplicator()
    assert d.is_duplicate("智慧黑板采购", "某中学", "100000", "2024-05-01") is False
    assert d.is_duplicate("智慧黑板采购", "某中学", "100000", "2024-05-01") is True
    assert d.checked == 2 and d.duplicates == 1


def test_deduplicate_iterator():
    rows = [
        {"title": "A", "procurement_unit": "U", "budget_amount": "1", "publish_date": "2024-01-01"},
        {"title": "A", "procurement_unit": "U", "budget_amount": "1", "publish_date": "2024-01-01"},
        {"title": "B", "procurement_unit": "U", "budget_amount": "2", "publish_date": "2024-01-02"},
    ]
    assert len(list(deduplicate(rows))) == 2

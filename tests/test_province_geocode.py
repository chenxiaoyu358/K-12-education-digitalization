"""Province-constrained geocoder: homonym / generic-name regressions found in review."""

from ztb.classification.province_geocode import load_province_gazetteers


def test_cross_province_homonyms_stay_in_province():
    g = load_province_gazetteers()
    assert g["340000"].resolve("太和县教育局", "").district_code == "341222"      # not 锦州太和区
    assert g["450000"].resolve("兴安县教育局", "").district_name == "兴安县"      # not 鹤岗兴安区
    r = g["440000"].resolve("东莞松山湖高新技术产业开发区管理委员会科技教育局", "")
    assert r.city_name == "东莞市"                                                # not 石家庄高新区


def test_within_province_homonym_needs_city():
    g = load_province_gazetteers()["510000"]
    assert g.resolve("乐山市市中区教育局", "").city_name == "乐山市"
    assert g.resolve("市中区实验小学", "").method == "province_only"


def test_prefix_rules_v1_2():
    g = load_province_gazetteers()
    assert g["510000"].resolve("高县教育和体育局", "").district_name == "高县"
    assert g["510000"].resolve("四川省大竹中学", "").district_name == "大竹县"
    assert g["510000"].resolve("提高县域教育质量项目", "").district_code is None


def test_stem_inside_longer_city_name():
    g = load_province_gazetteers()["450000"]
    assert g.resolve("防城港市第二中学", "").district_code is None

"""Worked example: classify and geocode procurement notices with the rule engine.

Self-contained — needs only this package (no dataset download).

    python examples/classify_jieba.py
"""

from ztb.classification.category import classify
from ztb.classification.geocode import default_geocoder

SAMPLES = [
    "广东省深圳市南山区南山小学交互式智能平板一体机采购项目",
    "北京市海淀区中关村第二小学校园无线网络升级改造",
    "某县教育局学生机房台式计算机采购",
    "某中学创客教室3D打印机及机器人套件采购",
    "某小学学生食堂大宗食材采购项目",          # non-ICT
]


def main() -> None:
    gc = default_geocoder()
    for title in SAMPLES:
        category = classify(title)
        geo = gc.geocode(title)
        print(f"- {title}")
        print(f"    category = {category.value}")
        print(f"    geo      = {geo.province_name or '-'} / {geo.city_name or '-'} / "
              f"{geo.district_name or '-'}  ({geo.resolution_level})")


if __name__ == "__main__":
    main()

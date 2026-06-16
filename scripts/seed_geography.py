"""Seed the database with Chinese administrative divisions.

Uses the Ministry of Civil Affairs standard codes (GB/T 2260).
Data source: http://www.mca.gov.cn/article/sj/xzqh/

Run: python scripts/seed_geography.py
"""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from sqlalchemy import select

from ztb.db.session import get_engine, get_session
from ztb.models import Base
from ztb.models.geography import City, District, Province

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "admin_divisions.json"

# Province short names
SHORT_NAMES = {
    "北京市": "京", "天津市": "津", "河北省": "冀", "山西省": "晋", "内蒙古自治区": "蒙",
    "辽宁省": "辽", "吉林省": "吉", "黑龙江省": "黑", "上海市": "沪", "江苏省": "苏",
    "浙江省": "浙", "安徽省": "皖", "福建省": "闽", "江西省": "赣", "山东省": "鲁",
    "河南省": "豫", "湖北省": "鄂", "湖南省": "湘", "广东省": "粤", "广西壮族自治区": "桂",
    "海南省": "琼", "重庆市": "渝", "四川省": "川", "贵州省": "贵", "云南省": "云",
    "西藏自治区": "藏", "陕西省": "陕", "甘肃省": "甘", "青海省": "青",
    "宁夏回族自治区": "宁", "新疆维吾尔自治区": "新",
}


def generate_seed_data() -> dict:
    """Generate seed data if JSON file doesn't exist.

    This creates a minimal but real dataset. For production, download
    the full dataset from stats.gov.cn or mca.gov.cn.
    """
    # 31 provinces/municipalities/autonomous regions with their codes
    provinces = {
        "110000": "北京市", "120000": "天津市", "130000": "河北省", "140000": "山西省",
        "150000": "内蒙古自治区", "210000": "辽宁省", "220000": "吉林省", "230000": "黑龙江省",
        "310000": "上海市", "320000": "江苏省", "330000": "浙江省", "340000": "安徽省",
        "350000": "福建省", "360000": "江西省", "370000": "山东省", "410000": "河南省",
        "420000": "湖北省", "430000": "湖南省", "440000": "广东省", "450000": "广西壮族自治区",
        "460000": "海南省", "500000": "重庆市", "510000": "四川省", "520000": "贵州省",
        "530000": "云南省", "540000": "西藏自治区", "610000": "陕西省", "620000": "甘肃省",
        "630000": "青海省", "640000": "宁夏回族自治区", "650000": "新疆维吾尔自治区",
    }
    data = {"provinces": []}
    for code, name in sorted(provinces.items()):
        data["provinces"].append({
            "code": code,
            "name": name,
            "short_name": SHORT_NAMES.get(name, ""),
            "cities": [],  # To be populated with real data
        })
    return data


def seed(session) -> None:
    """Seed provinces, cities, and districts from JSON data."""
    if not DATA_FILE.exists():
        print(f"Generating seed data file: {DATA_FILE}")
        data = generate_seed_data()
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        data = json.loads(DATA_FILE.read_text(encoding="utf-8"))

    for prov_data in data["provinces"]:
        existing = session.execute(
            select(Province).where(Province.code == prov_data["code"])
        ).scalar_one_or_none()
        if existing:
            province = existing
        else:
            province = Province(
                name=prov_data["name"],
                code=prov_data["code"],
                short_name=prov_data.get("short_name", ""),
            )
            session.add(province)
            session.flush()
            print(f"  + Province: {province.name}")

        for city_data in prov_data.get("cities", []):
            existing_city = session.execute(
                select(City).where(City.code == city_data["code"])
            ).scalar_one_or_none()
            if existing_city:
                city = existing_city
            else:
                city = City(
                    province_id=province.id,
                    name=city_data["name"],
                    code=city_data["code"],
                )
                session.add(city)
                session.flush()

            for dist_data in city_data.get("districts", []):
                existing_dist = session.execute(
                    select(District).where(District.code == dist_data["code"])
                ).scalar_one_or_none()
                if not existing_dist:
                    district = District(
                        city_id=city.id,
                        name=dist_data["name"],
                        code=dist_data["code"],
                    )
                    session.add(district)

    session.commit()
    count_p = session.query(Province).count()
    count_c = session.query(City).count()
    count_d = session.query(District).count()
    print(f"\nSeeded: {count_p} provinces, {count_c} cities, {count_d} districts")


if __name__ == "__main__":
    engine = get_engine()
    Base.metadata.create_all(engine)
    session = get_session()
    try:
        seed(session)
    finally:
        session.close()

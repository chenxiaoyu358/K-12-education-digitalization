"""File-backed GB/T 2260 geocoder (no database required).

The production geocoder resolves administrative codes against a seeded PostgreSQL
``geography`` table; this dependency-free variant loads ``data/admin_divisions.json``
(the same GB/T 2260 seed deposited as Companion File 4) and resolves the names extracted
by :func:`ztb.classification.geography.extract_geography` to province / city / district
codes. It lets the worked examples run without standing up Postgres.

    >>> from ztb.classification.geocode import Geocoder
    >>> Geocoder().geocode("广东省深圳市南山区南山小学")
    GeoCode(province_code='440000', province_name='广东省', city_code='440300', ...)
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

from ztb.classification.geography import (
    PROVINCE_SHORT_MAP,
    GeoMatch,
    extract_geography,
)

_DATA = Path(__file__).resolve().parent.parent.parent.parent / "data" / "admin_divisions.json"


@dataclass(frozen=True)
class GeoCode:
    province_code: Optional[str] = None
    province_name: Optional[str] = None
    city_code: Optional[str] = None
    city_name: Optional[str] = None
    district_code: Optional[str] = None
    district_name: Optional[str] = None

    @property
    def resolution_level(self) -> str:
        if self.district_code:
            return "district"
        if self.city_code:
            return "city"
        if self.province_code:
            return "province"
        return "unresolved"


def _norm(name: str) -> str:
    """Drop common admin suffixes so '广东省' matches '广东', '深圳市' matches '深圳'."""
    for suf in ("特别行政区", "自治区", "自治州", "地区", "盟", "省", "市", "区", "县", "旗", "州"):
        if name.endswith(suf) and len(name) > len(suf):
            return name[: -len(suf)]
    return name


class Geocoder:
    """Resolve extracted geography names to GB/T 2260 codes via the JSON seed."""

    def __init__(self, data_path: Path | str = _DATA) -> None:
        self._provinces, self._cities, self._districts = self._build(Path(data_path))

    @staticmethod
    def _build(path: Path):
        data = json.loads(path.read_text(encoding="utf-8"))
        provinces: dict[str, tuple[str, str]] = {}      # norm name -> (code, name)
        cities: dict[str, dict[str, tuple[str, str]]] = {}    # prov_code -> {norm: (code,name)}
        districts: dict[str, dict[str, tuple[str, str]]] = {}  # city_code -> {norm: (code,name)}
        for prov in data["provinces"]:
            pcode, pname = prov["code"], prov["name"]
            provinces[_norm(pname)] = (pcode, pname)
            cities.setdefault(pcode, {})
            for city in prov.get("cities", []):
                ccode, cname = city["code"], city["name"]
                cities[pcode][_norm(cname)] = (ccode, cname)
                districts.setdefault(ccode, {})
                for dist in city.get("districts", []):
                    districts[ccode][_norm(dist["name"])] = (dist["code"], dist["name"])
        return provinces, cities, districts

    def geocode_match(self, geo: GeoMatch) -> GeoCode:
        pcode = pname = ccode = cname = dcode = dname = None

        if geo.province:
            key = _norm(geo.province)
            key = _norm(PROVINCE_SHORT_MAP.get(key, key))
            if key in self._provinces:
                pcode, pname = self._provinces[key]

        if pcode and geo.city:
            hit = self._cities.get(pcode, {}).get(_norm(geo.city))
            if hit:
                ccode, cname = hit
        elif geo.city and not pcode:
            # search city across all provinces (first exact match wins)
            for pc, table in self._cities.items():
                hit = table.get(_norm(geo.city))
                if hit:
                    pcode, pname = next((v for k, v in self._provinces.items()
                                         if v[0] == pc), (None, None))
                    ccode, cname = hit
                    break

        if ccode and geo.district:
            hit = self._districts.get(ccode, {}).get(_norm(geo.district))
            if hit:
                dcode, dname = hit
        elif pcode and not ccode and geo.district:
            # Municipalities (北京/天津/上海/重庆): districts sit under a 市辖区 city.
            for cc, cn in self._cities.get(pcode, {}).values():
                hit = self._districts.get(cc, {}).get(_norm(geo.district))
                if hit:
                    ccode, cname = cc, cn
                    dcode, dname = hit
                    break

        return GeoCode(pcode, pname, ccode, cname, dcode, dname)

    def geocode(self, text: str) -> GeoCode:
        """Extract geography from free text and resolve to codes in one step."""
        return self.geocode_match(extract_geography(text))


@lru_cache(maxsize=1)
def default_geocoder() -> Geocoder:
    return Geocoder()

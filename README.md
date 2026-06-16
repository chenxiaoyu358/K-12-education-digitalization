# ztb-classify

This repository contains the deterministic, model-free processing logic used to turn raw
Chinese government procurement notices into the deposited dataset:

| Component | Module |
|---|---|
| jieba rule engine (11 ICT categories) | `src/ztb/classification/category.py`, `keywords.py` |
| non-ICT pattern pre-filter | `src/ztb/classification/non_ict_rules.py` |
| GB/T 2260 geocoder (file-backed, no DB) | `src/ztb/classification/geocode.py`, `geography.py` |
| SHA-256 deduplicator | `src/ztb/utils/dedup.py`, `hash.py` |
| buyer-type classifier + curation utils | `src/ztb/classification/unit_type.py`, `src/ztb/utils/{dates,money,text}.py` |
| GB/T 2260 geography seed (optional DB path) | `scripts/seed_geography.py`, `data/admin_divisions.json` |

The classifier is **fully deterministic and auditable**: every category assignment traces
to a specific keyword in `data/keyword_dicts/` (697 keywords across 11 ICT category files
plus a 308-term `non_ict.txt` exclusion list). A large language model was used only to
diagnose keyword gaps while *building* the dictionary; it plays no role at inference.

## Install

```bash
pip install -e .            # core: jieba + w3lib
pip install -e ".[data]"    # + pandas/pyarrow/frictionless/mlcroissant for the loaders
pip install -e ".[dev]"     # + pytest/ruff
```

Python ≥ 3.11.

## Quickstart — classify and geocode

```python
from ztb.classification.category import classify
from ztb.classification.geocode import default_geocoder

classify("广东省深圳市南山区南山小学交互式智能平板一体机采购项目")
# Category.MULTIMEDIA_DISPLAY

default_geocoder().geocode("广东省深圳市南山区教育局")
# GeoCode(province_code='440000', city_code='440300', district_code='440305', ...)
```

Deduplicate an iterable of records by content hash:

```python
from ztb.utils.dedup import deduplicate
unique = list(deduplicate(records))   # collapses exact cross-source mirrors
```

## Worked examples for the deposited dataset

Download the dataset (Companion File 1) and metadata (Companion File 3) from Figshare
(DOI: `[FIGSHARE-DOI]`) and keep the deposit folder layout, then:

```bash
python examples/classify_jieba.py                                   # no download needed
python examples/load_pandas.py       CF1_dataset/k12_ict_procurement_2022_2025.parquet
python examples/load_frictionless.py CF3_metadata/datapackage.json
python examples/load_croissant.py    CF3_metadata/croissant.json
```

The dataset has **227,649 records × 29 fields**. To compute project-level totals, group by
`project_id` and apply the stage preference **contract > result > correction >
announcement** (see `examples/load_pandas.py`).

## Reusing the dictionary on another corpus

The keyword files are plain text (one keyword per line, `#` comments ignored) and load
directly into jieba:

```python
from ztb.classification.keywords import load_all_keyword_dicts
dicts = load_all_keyword_dicts()      # {category: [keyword, ...]}
```

## Geography seed (optional database path)

`geocode.py` resolves codes directly from `data/admin_divisions.json` and needs no
database. The production pipeline instead seeds a PostgreSQL `geography` table; reproduce
that with `python scripts/seed_geography.py` (requires a configured database).

## Tests

```bash
pytest
```

## Licensing & citation

- **Code:** MIT (this repository).
- **Dataset:** CC BY 4.0 (Figshare deposit).

Please cite both the Data Descriptor and the Figshare deposit when using the data or code.
The exact commit producing the deposited dataset is tagged `v1.0`.

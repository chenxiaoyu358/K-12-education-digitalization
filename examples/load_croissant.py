"""Worked example: load the dataset as an ML-ready Croissant dataset.

Download Companion File 1 (data) and Companion File 3 (metadata) and keep the deposit
layout so the contentUrl inside croissant.json resolves, then:

    python examples/load_croissant.py path/to/CF3_metadata/croissant.json
"""

import sys

import mlcroissant as mlc


def main(jsonld: str) -> None:
    ds = mlc.Dataset(jsonld=jsonld)
    print(f"dataset: {ds.metadata.name}")

    print("\nfirst 3 records:")
    for i, rec in enumerate(ds.records(record_set="records")):
        if i >= 3:
            break
        # Croissant returns bytes for text fields; decode for display.
        rid = rec["records/record_id"]
        cat = rec["records/category"]
        cat = cat.decode() if isinstance(cat, bytes) else cat
        print(f"  {rid}  {cat}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: python examples/load_croissant.py <croissant.json>")
    main(sys.argv[1])

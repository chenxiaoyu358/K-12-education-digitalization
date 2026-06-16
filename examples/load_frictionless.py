"""Worked example: load the dataset through its Frictionless data package.

Download Companion File 1 (data) and Companion File 3 (metadata) and keep the deposit
layout so the relative resource paths inside datapackage.json resolve, then:

    python examples/load_frictionless.py path/to/CF3_metadata/datapackage.json
"""

import sys

from frictionless import Package


def main(descriptor: str) -> None:
    pkg = Package(descriptor)
    print("resources:")
    for res in pkg.resources:
        print(f"  - {res.name}  ({res.format})")

    res = pkg.get_resource("k12_ict_procurement_2022_2025")
    print(f"\nschema: {len(res.schema.fields)} fields; "
          f"primary key = {res.schema.primary_key}")

    print("\nfirst 3 rows:")
    with res:
        for i, row in enumerate(res.row_stream):
            if i >= 3:
                break
            print(f"  {row['record_id']}  {row['category']:18s}  {str(row['title'])[:40]}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: python examples/load_frictionless.py <datapackage.json>")
    main(sys.argv[1])

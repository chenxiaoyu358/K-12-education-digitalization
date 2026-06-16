"""Worked example: load the deposited dataset with pandas.

Download the dataset (Companion File 1) from Figshare first, then point this script at
the CSV or Parquet file.

    python examples/load_pandas.py path/to/k12_ict_procurement_2022_2025.parquet
"""

import sys

import pandas as pd

STAGE_RANK = {"contract": 0, "result": 1, "correction": 2, "announcement": 3}


def main(path: str) -> None:
    df = pd.read_parquet(path) if path.endswith(".parquet") else pd.read_csv(path)
    print(f"loaded {len(df):,} rows x {len(df.columns)} cols")
    print("\nrecords per ICT category:")
    print(df["category"].value_counts())

    # Project-level totals: one canonical notice per project (stage preference
    # contract > result > correction > announcement), then sum budgets.
    df["_rank"] = df["stage"].map(STAGE_RANK).fillna(9)
    canonical = df.sort_values("_rank").drop_duplicates("project_id", keep="first")
    print(f"\n{df['project_id'].nunique():,} distinct projects "
          f"({len(canonical):,} canonical notices)")
    total = canonical["budget_amount"].dropna().sum()
    print(f"summed budget over canonical notices: CNY {total:,.0f}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("usage: python examples/load_pandas.py <dataset.csv|.parquet>")
    main(sys.argv[1])

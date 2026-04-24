#!/usr/bin/env python3
"""
Extract the most-significant additive-test variants from a PLINK .assoc.logistic file.

Output is a sorted TSV of top hits, ready for downstream eQTL annotation.

Usage:
  python scripts/extract_top_gwas_hits.py \
      --gwas  ../06_asthma_gwas/results/asthma_gwas.assoc.logistic \
      --out   results/top_gwas_hits.tsv \
      --top-n 20
"""

import argparse
import io
import sys

import pandas as pd

REQUIRED_COLS = {"TEST", "SNP", "A1", "OR", "P"}


def _read_assoc_logistic(path: str) -> pd.DataFrame:
    """
    Read a PLINK .assoc.logistic file.
    PLINK writes a leading space on the header line; stripping each line before
    parsing avoids a phantom empty first column in pandas.
    """
    try:
        with open(path) as fh:
            content = "\n".join(line.rstrip("\n").lstrip() for line in fh)
    except FileNotFoundError:
        sys.exit(f"Error: file not found: {path}")
    return pd.read_csv(io.StringIO(content), sep=r"\s+", engine="python")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extract top GWAS hits from a PLINK .assoc.logistic file",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--gwas", required=True,
        help="PLINK .assoc.logistic file (columns: CHR SNP BP A1 TEST NMISS OR STAT P)",
    )
    parser.add_argument(
        "--out", required=True,
        help="Output TSV path",
    )
    parser.add_argument(
        "--p-threshold", type=float, default=None,
        help="Optional P-value ceiling; if omitted all variants are kept before --top-n",
    )
    parser.add_argument(
        "--top-n", type=int, default=20,
        help="Number of top variants to retain (ranked by ascending P)",
    )
    args = parser.parse_args()

    if args.top_n < 1:
        sys.exit("Error: --top-n must be a positive integer.")
    if args.p_threshold is not None and not (0 < args.p_threshold <= 1):
        sys.exit("Error: --p-threshold must be in the range (0, 1].")

    # ---- Load ----
    df = _read_assoc_logistic(args.gwas)
    print(f"Loaded {len(df):,} rows from {args.gwas}")

    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        sys.exit(
            f"Error: required column(s) missing: {sorted(missing)}\n"
            f"  Columns present: {list(df.columns)}"
        )

    # ---- Filter to additive test ----
    df = df[df["TEST"] == "ADD"].copy()
    if df.empty:
        sys.exit("Error: no ADD rows found. Verify input is a PLINK --logistic output.")
    print(f"  After TEST==ADD filter: {len(df):,} variants")

    # ---- Coerce numeric columns; drop rows with invalid OR or P ----
    df["OR"] = pd.to_numeric(df["OR"], errors="coerce")
    df["P"]  = pd.to_numeric(df["P"],  errors="coerce")
    bad_or = df["OR"].isna() | (df["OR"] <= 0)
    bad_p  = df["P"].isna()
    n_dropped = (bad_or | bad_p).sum()
    if n_dropped:
        print(f"  Dropped {n_dropped} rows with invalid OR or P")
    df = df[~(bad_or | bad_p)].copy()

    # ---- Optional p-value threshold ----
    if args.p_threshold is not None:
        df = df[df["P"] <= args.p_threshold].copy()
        print(f"  After P <= {args.p_threshold}: {len(df):,} variants")
        if df.empty:
            sys.exit(
                f"Error: no variants pass P <= {args.p_threshold}.\n"
                f"  Try a less strict --p-threshold or omit it entirely."
            )

    # ---- Sort and cap ----
    df = df.sort_values("P").head(args.top_n).reset_index(drop=True)
    print(f"  Retaining top {len(df)} variants")

    keep = [c for c in ["CHR", "SNP", "BP", "A1", "OR", "STAT", "P"] if c in df.columns]
    df[keep].to_csv(args.out, sep="\t", index=False)
    print(f"Top hits written: {args.out}")


if __name__ == "__main__":
    main()

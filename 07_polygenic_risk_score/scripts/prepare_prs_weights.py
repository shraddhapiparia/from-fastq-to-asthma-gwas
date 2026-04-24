#!/usr/bin/env python3
"""
Derive a PLINK2 --score weight file from a PLINK .assoc.logistic result.

Processing steps:
  1. Read the association file (space-delimited, handles PLINK leading-space header)
  2. Keep only TEST == "ADD" rows
  3. Drop rows with invalid OR (<= 0, NA) or invalid P (NA, out of [0,1])
  4. Compute BETA = ln(OR)  — the natural log converts the odds ratio to the
     log-odds scale expected by standard PRS scoring
  5. Filter to P <= p_threshold
  6. Sort ascending by P; optionally cap to --top-n variants
  7. Write PLINK2 score file:  SNP  A1  BETA  (tab-separated, with header)
  8. Write human-readable summary: original GWAS columns + computed BETA

Outputs:
  <out>                   PLINK2 score file
  <out>.replace(.tsv, _summary.tsv)   human-readable summary
"""

import argparse
import io
import sys

import numpy as np
import pandas as pd

REQUIRED_COLS = {"TEST", "SNP", "A1", "OR", "P"}


def read_assoc_logistic(path: str) -> pd.DataFrame:
    """
    Read a PLINK .assoc.logistic file.
    PLINK writes a leading space on the header line; stripping each line before
    parsing prevents pandas from creating a phantom empty first column.
    """
    try:
        with open(path) as fh:
            content = "\n".join(line.rstrip("\n").lstrip() for line in fh)
    except FileNotFoundError:
        sys.exit(f"Error: GWAS file not found: {path}")

    df = pd.read_csv(io.StringIO(content), sep=r"\s+", engine="python")
    return df


def validate_columns(df: pd.DataFrame, path: str) -> None:
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        sys.exit(
            f"Error: required column(s) not found in {path}: {sorted(missing)}\n"
            f"  Columns present: {list(df.columns)}\n"
            f"  Expected format: CHR SNP BP A1 TEST NMISS OR STAT P"
        )


def summary_path_for(out: str) -> str:
    """Derive the human-readable summary path from the score file path."""
    if out.endswith(".tsv"):
        return out[:-4] + "_summary.tsv"
    return out + "_summary.tsv"


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Convert a PLINK .assoc.logistic file to a PLINK2 --score weight file. "
            "Filters by p-value, computes BETA = ln(OR), and writes a score file "
            "plus a human-readable summary."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--gwas", required=True,
        help="PLINK .assoc.logistic file (columns: CHR SNP BP A1 TEST NMISS OR STAT P)",
    )
    parser.add_argument(
        "--out", required=True,
        help="Output path for PLINK2 score file (SNP  A1  BETA, tab-separated with header)",
    )
    parser.add_argument(
        "--p-threshold", type=float, default=0.05,
        help="Maximum P-value for including a variant",
    )
    parser.add_argument(
        "--top-n", type=int, default=None,
        help=(
            "After the p-threshold filter, keep only the top N variants ranked by P. "
            "Applied after sorting, so N=10 gives the 10 most-significant passing variants."
        ),
    )
    args = parser.parse_args()

    # ---- Validate CLI args ----
    if not (0 < args.p_threshold <= 1):
        sys.exit("Error: --p-threshold must be in the range (0, 1].")
    if args.top_n is not None and args.top_n < 1:
        sys.exit("Error: --top-n must be a positive integer.")

    # ---- Load ----
    df = read_assoc_logistic(args.gwas)
    validate_columns(df, args.gwas)
    print(f"Loaded {len(df):,} rows from {args.gwas}")

    # ---- Keep additive test rows only ----
    df = df[df["TEST"] == "ADD"].copy()
    if df.empty:
        sys.exit(
            "Error: no rows with TEST == 'ADD' found.\n"
            "  Verify the input is a PLINK --logistic output file."
        )
    print(f"  After TEST==ADD filter:         {len(df):>6,} variants")

    # ---- Drop rows with invalid OR or P ----
    df["OR"] = pd.to_numeric(df["OR"], errors="coerce")
    df["P"]  = pd.to_numeric(df["P"],  errors="coerce")

    bad_or = df["OR"].isna() | (df["OR"] <= 0)
    bad_p  = df["P"].isna()  | (df["P"] < 0) | (df["P"] > 1)
    n_dropped = (bad_or | bad_p).sum()
    df = df[~(bad_or | bad_p)].copy()

    if n_dropped:
        print(f"  Dropped {n_dropped} rows with invalid OR or P")
    if df.empty:
        sys.exit("Error: no valid variants remain after removing rows with invalid OR/P.")

    # ---- Compute BETA = ln(OR) ----
    # OR is the multiplicative effect per copy of A1.
    # PLINK2 --score expects additive log-odds weights (BETA).
    # ln(OR) converts from the multiplicative to the additive log-odds scale.
    df["BETA"] = np.log(df["OR"])

    # ---- P-value filter ----
    df_pass = df[df["P"] <= args.p_threshold].copy()
    if df_pass.empty:
        sys.exit(
            f"Error: no variants pass P <= {args.p_threshold}.\n"
            f"  Minimum P in file: {df['P'].min():.4g}\n"
            f"  Suggestion: raise --p-threshold (e.g. --p-threshold 0.5) or "
            f"check that the input is the right file."
        )
    print(f"  After P <= {args.p_threshold} filter:          {len(df_pass):>6,} variants")

    # ---- Sort by P (ascending), then optionally cap ----
    df_pass = df_pass.sort_values("P").reset_index(drop=True)
    if args.top_n is not None and len(df_pass) > args.top_n:
        print(f"  Applying --top-n {args.top_n} (from {len(df_pass)} passing variants)")
        df_pass = df_pass.head(args.top_n)

    print(f"  Final variant count:            {len(df_pass):>6,}")

    # ---- Write PLINK2 score file ----
    score_df = df_pass[["SNP", "A1", "BETA"]]
    score_df.to_csv(args.out, sep="\t", index=False)
    print(f"\nPLINK2 score file written:    {args.out}")

    # ---- Write human-readable summary ----
    summ_path = summary_path_for(args.out)
    keep = [c for c in ["CHR", "SNP", "BP", "A1", "NMISS", "OR", "STAT", "P", "BETA"]
            if c in df_pass.columns]
    df_pass[keep].to_csv(summ_path, sep="\t", index=False, float_format="%.6g")
    print(f"Human-readable summary written: {summ_path}")

    # ---- Sanity summary ----
    n_risk = int((df_pass["BETA"] > 0).sum())
    n_prot = int((df_pass["BETA"] < 0).sum())
    print(
        f"\n  Risk-increasing variants (OR > 1, BETA > 0): {n_risk}\n"
        f"  Protective variants     (OR < 1, BETA < 0): {n_prot}\n"
        f"  BETA range: {df_pass['BETA'].min():.4f}  to  {df_pass['BETA'].max():.4f}"
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Merge PLINK2 .sscore output with a phenotype file.

Outputs:
  <out>               merged TSV (one row per sample, PRS + phenotype columns)
  <out>_summary.tsv   per-group summary statistics (mean, SD, median, min, max)
"""

import argparse
import sys
import pandas as pd

# Column name candidates for sample ID and phenotype across common formats
_ID_COLS    = ["IID", "iid", "id", "sample", "sample_id", "SampleID", "SAMPLE_ID"]
_PHENO_COLS = ["PHENO", "pheno", "phenotype", "PHENOTYPE"]
# PLINK 1/2 phenotype coding
_PLINK_LABELS = {1: "control", 2: "case", 1.0: "control", 2.0: "case"}


def _find_col(df: pd.DataFrame, candidates: list) -> str | None:
    """Return the first column name in df that appears in candidates, else None."""
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _read_table(path: str) -> pd.DataFrame:
    """Read a TSV, CSV, or space-delimited file (handles PLINK .profile and .sscore)."""
    df = pd.read_csv(path, sep="\t")
    if df.shape[1] < 2:
        df = pd.read_csv(path, sep=",")
    if df.shape[1] < 2:
        # PLINK 1.9 .profile files are space-delimited with a leading-space header
        df = pd.read_csv(path, sep=r"\s+", engine="python")
    # Strip PLINK-style '#' prefix from column headers (e.g. '#FID', '#IID')
    df.columns = [c.lstrip("#") for c in df.columns]
    return df


def main():
    parser = argparse.ArgumentParser(
        description="Merge PLINK2 .sscore with a phenotype file"
    )
    parser.add_argument("--sscore", required=True,
                        help="PLINK2 .sscore file")
    parser.add_argument("--pheno",  required=True,
                        help="Phenotype file (TSV or CSV, must contain IID and PHENO)")
    parser.add_argument("--out",    required=True,
                        help="Output path for merged TSV")
    args = parser.parse_args()

    # ---- Load .sscore ----
    scores = _read_table(args.sscore)

    # Find the SCORE column (PLINK2 default: SCORE1_AVG; may vary by version)
    score_cols = [c for c in scores.columns if c.upper().startswith("SCORE")]
    if not score_cols:
        sys.exit(
            "Error: no SCORE* column found in .sscore. "
            "Confirm plink2 produced a valid .sscore output."
        )
    score_col = score_cols[0]

    sscore_id = _find_col(scores, _ID_COLS)
    if sscore_id is None:
        sys.exit(
            f"Error: no recognised ID column in .sscore. "
            f"Columns present: {list(scores.columns)}"
        )

    scores = (
        scores[[sscore_id, score_col]]
        .rename(columns={sscore_id: "IID", score_col: "PRS"})
    )

    # ---- Load phenotype ----
    pheno = _read_table(args.pheno)

    pheno_id = _find_col(pheno, _ID_COLS)
    if pheno_id is None:
        sys.exit(
            f"Error: no recognised ID column in phenotype file. "
            f"Columns present: {list(pheno.columns)}"
        )
    pheno = pheno.rename(columns={pheno_id: "IID"})

    # ---- Merge ----
    merged = pd.merge(scores, pheno, on="IID", how="inner")
    if merged.empty:
        print(
            "Warning: merge produced 0 rows. "
            "Check that IID values match between .sscore and phenotype file.",
            file=sys.stderr,
        )

    merged.to_csv(args.out, sep="\t", index=False)
    print(f"Merged table:  {args.out}  ({len(merged)} samples)")

    # ---- Summary statistics ----
    summary_path = args.out.replace("_merged.tsv", "_summary.tsv")
    # Fall back to a generic path if the input doesn't end in _merged.tsv
    if summary_path == args.out:
        summary_path = args.out.replace(".tsv", "_summary.tsv")

    pheno_col = _find_col(merged, _PHENO_COLS)
    if pheno_col:
        unique_vals = set(merged[pheno_col].dropna().unique())
        if unique_vals.issubset({1, 2, 1.0, 2.0}):
            merged["_group"] = merged[pheno_col].map(_PLINK_LABELS)
        else:
            merged["_group"] = merged[pheno_col].astype(str)

        summary = (
            merged.groupby("_group")["PRS"]
            .agg(n="count", mean="mean", sd="std",
                 median="median", min="min", max="max")
            .reset_index()
            .rename(columns={"_group": "group"})
        )
    else:
        summary = pd.DataFrame([{
            "group":  "all",
            "n":      len(merged),
            "mean":   merged["PRS"].mean(),
            "sd":     merged["PRS"].std(),
            "median": merged["PRS"].median(),
            "min":    merged["PRS"].min(),
            "max":    merged["PRS"].max(),
        }])

    summary.to_csv(summary_path, sep="\t", index=False, float_format="%.6f")
    print(f"Summary stats: {summary_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Annotate top GWAS hits with eQTL information via a simple SNP-ID lookup.

Performs a left join of GWAS hits onto an eQTL reference table.
All GWAS hits are retained; SNPs absent from the reference receive the
label "No eQTL match in demo reference".

This is annotation-based prioritisation, not formal statistical colocalization.
A SNP appearing in both tables does not confirm that the GWAS and eQTL signals
are the same causal variant.

Outputs:
  <out>_candidates.tsv    full merged table (all GWAS hits + eQTL columns where matched)
  <out>_prioritized.tsv   matched hits only, sorted by GWAS P, with interpretation column

Usage:
  python scripts/map_gwas_to_eqtl.py \
      --gwas-hits  results/top_gwas_hits.tsv \
      --eqtl-ref   data/demo_eqtl_reference.tsv \
      --out        results/eqtl_annotation
"""

import argparse
import sys

import pandas as pd


def _interpretation(row: pd.Series) -> str:
    """Generate a one-line prioritization hypothesis for a merged row."""
    if pd.isna(row.get("eQTL_gene")):
        return "No eQTL match in demo reference"
    direction   = "higher" if row["eqtl_beta"] > 0 else "lower"
    allele_type = "risk" if row["OR"] > 1 else "protective"
    return (
        f"Candidate: {allele_type} allele ({row['A1']}) co-localises with "
        f"{direction} {row['eQTL_gene']} expression in {row['tissue']} "
        f"(demo annotation only)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Annotate GWAS top hits with eQTL reference data",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--gwas-hits", required=True,
        help="Top GWAS hits TSV (output of extract_top_gwas_hits.py)",
    )
    parser.add_argument(
        "--eqtl-ref", required=True,
        help="eQTL reference TSV (columns: SNP, eQTL_gene, tissue, eqtl_beta, source)",
    )
    parser.add_argument(
        "--out", required=True,
        help="Output prefix; writes <out>_candidates.tsv and <out>_prioritized.tsv",
    )
    args = parser.parse_args()

    # ---- Load GWAS hits ----
    try:
        gwas = pd.read_csv(args.gwas_hits, sep="\t")
    except FileNotFoundError:
        sys.exit(f"Error: GWAS hits file not found: {args.gwas_hits}")
    if "SNP" not in gwas.columns:
        sys.exit(
            f"Error: 'SNP' column not found in {args.gwas_hits}.\n"
            f"  Columns present: {list(gwas.columns)}"
        )

    # ---- Load eQTL reference ----
    try:
        eqtl = pd.read_csv(args.eqtl_ref, sep="\t")
    except FileNotFoundError:
        sys.exit(f"Error: eQTL reference file not found: {args.eqtl_ref}")
    for col in ["SNP", "eQTL_gene", "tissue", "eqtl_beta"]:
        if col not in eqtl.columns:
            sys.exit(
                f"Error: required column '{col}' not found in {args.eqtl_ref}.\n"
                f"  Columns present: {list(eqtl.columns)}"
            )

    print(f"GWAS hits:    {len(gwas):>4} variants")
    print(f"eQTL entries: {len(eqtl):>4} records in reference")

    # ---- Left join on SNP ----
    merged = pd.merge(gwas, eqtl, on="SNP", how="left")
    n_matched   = merged["eQTL_gene"].notna().sum()
    n_unmatched = len(merged) - n_matched
    print(f"Matched:      {n_matched:>4} variants have eQTL annotations")
    print(f"Unmatched:    {n_unmatched:>4} variants have no match in demo reference")

    # ---- Interpretation column ----
    merged["interpretation"] = merged.apply(_interpretation, axis=1)

    # ---- Write candidates (full merged table) ----
    candidates_path = f"{args.out}_candidates.tsv"
    merged.to_csv(candidates_path, sep="\t", index=False, float_format="%.6g")
    print(f"\nCandidates table:  {candidates_path}  ({len(merged)} rows)")

    # ---- Write prioritized (matched only, sorted by P) ----
    prioritized_cols = [
        c for c in
        ["SNP", "A1", "CHR", "BP", "OR", "P",
         "eQTL_gene", "tissue", "eqtl_beta", "source", "interpretation"]
        if c in merged.columns
    ]
    prioritized = (
        merged.loc[merged["eQTL_gene"].notna(), prioritized_cols]
        .sort_values("P")
        .reset_index(drop=True)
    )
    prioritized_path = f"{args.out}_prioritized.tsv"
    prioritized.to_csv(prioritized_path, sep="\t", index=False, float_format="%.6g")
    print(f"Prioritized table: {prioritized_path}  ({len(prioritized)} matched variants)")

    if prioritized.empty:
        print(
            "\nNote: no SNPs matched the demo reference. Replace "
            "data/demo_eqtl_reference.tsv with a real eQTL resource "
            "containing your variant IDs."
        )
    else:
        print("\nTop prioritized variant:")
        top = prioritized.iloc[0]
        print(f"  {top['SNP']}  P={top['P']:.4g}  → {top['interpretation']}")


if __name__ == "__main__":
    main()

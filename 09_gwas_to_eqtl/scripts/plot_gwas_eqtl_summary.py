#!/usr/bin/env python3
"""
Visualise GWAS-to-eQTL prioritization results.

Reads the candidates table (output of map_gwas_to_eqtl.py) and produces a
horizontal bar chart of -log10(P) per variant, coloured by eQTL gene
annotation. Unmatched variants are shown in grey.

Output:
  <out-dir>/gwas_eqtl_summary.png

Usage:
  python scripts/plot_gwas_eqtl_summary.py \
      --candidates results/eqtl_annotation_candidates.tsv \
      --out-dir    results/figures
"""

import argparse
import math
import os
import sys

import pandas as pd
import matplotlib
matplotlib.use("Agg")   # non-interactive backend; set before importing pyplot
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

_NO_MATCH_COLOUR = "#BBBBBB"
_GENE_PALETTE    = [
    "#4393C3", "#D6604D", "#74C476", "#FD8D3C",
    "#9E9AC8", "#FDAE6B", "#E7969C", "#9ECAE1",
]


def _build_colour_map(gene_labels: list) -> dict:
    colour_map = {}
    palette_idx = 0
    for g in sorted(gene_labels):
        if g == "No match":
            colour_map[g] = _NO_MATCH_COLOUR
        else:
            colour_map[g] = _GENE_PALETTE[palette_idx % len(_GENE_PALETTE)]
            palette_idx += 1
    return colour_map


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plot GWAS-to-eQTL prioritization summary"
    )
    parser.add_argument(
        "--candidates", required=True,
        help="Candidates TSV (output of map_gwas_to_eqtl.py)",
    )
    parser.add_argument(
        "--out-dir", required=True,
        help="Directory for output figure",
    )
    parser.add_argument(
        "--prefix", default=None,
        help="Optional filename prefix; saves as <prefix>_gwas_eqtl_summary.png",
    )
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    try:
        df = pd.read_csv(args.candidates, sep="\t")
    except FileNotFoundError:
        sys.exit(f"Error: file not found: {args.candidates}")

    for col in ["SNP", "P"]:
        if col not in df.columns:
            sys.exit(f"Error: required column '{col}' not found in {args.candidates}.")

    df["P"] = pd.to_numeric(df["P"], errors="coerce")
    df = df.dropna(subset=["P"]).reset_index(drop=True)

    if df.empty:
        sys.exit("Error: no rows with valid P-values found.")

    df["neg_log_p"] = df["P"].apply(lambda p: -math.log10(p) if p > 0 else 0)

    # eQTL gene label for display
    if "eQTL_gene" in df.columns:
        df["gene_label"] = df["eQTL_gene"].fillna("No match")
    else:
        df["gene_label"] = "No match"

    colour_map = _build_colour_map(df["gene_label"].unique().tolist())
    df["colour"] = df["gene_label"].map(colour_map)

    # Sort: least significant at bottom, most significant at top
    df_plot = df.sort_values("neg_log_p", ascending=True).reset_index(drop=True)

    fig_height = max(4, 0.45 * len(df_plot))
    fig, ax = plt.subplots(figsize=(9, fig_height))

    bars = ax.barh(
        df_plot["SNP"],
        df_plot["neg_log_p"],
        color=df_plot["colour"],
        edgecolor="white",
        linewidth=0.4,
        height=0.7,
    )

    # Annotate matched bars with gene name
    x_max = df_plot["neg_log_p"].max()
    for bar, (_, row) in zip(bars, df_plot.iterrows()):
        if row["gene_label"] != "No match":
            ax.text(
                bar.get_width() + x_max * 0.02,
                bar.get_y() + bar.get_height() / 2,
                row["gene_label"],
                va="center",
                ha="left",
                fontsize=8,
                color="#333333",
            )

    ax.set_xlabel(r"$-\log_{10}(P)$", fontsize=12)
    ax.set_ylabel("Variant", fontsize=12)
    ax.set_title("Top GWAS Hits with eQTL Annotations — Demo", fontsize=13)
    ax.spines[["top", "right"]].set_visible(False)
    # Extra right margin for gene labels
    ax.set_xlim(right=x_max * 1.35)

    # Legend: matched genes first, then "No match"
    legend_order = sorted(
        colour_map.keys(), key=lambda g: (g == "No match", g)
    )
    legend_handles = [
        Patch(facecolor=colour_map[g], label=g) for g in legend_order
    ]
    ax.legend(
        handles=legend_handles,
        title="eQTL gene",
        bbox_to_anchor=(1.02, 1),
        loc="upper left",
        frameon=False,
        fontsize=9,
    )

    fig.tight_layout()
    fname    = f"{args.prefix}_gwas_eqtl_summary.png" if args.prefix else "gwas_eqtl_summary.png"
    out_path = os.path.join(args.out_dir, fname)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Figure saved: {out_path}")


if __name__ == "__main__":
    main()

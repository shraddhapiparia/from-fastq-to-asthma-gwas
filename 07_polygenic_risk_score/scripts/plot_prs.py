#!/usr/bin/env python3
"""
Plot PRS distribution from a merged PRS + phenotype TSV.

Outputs (written to --out-dir):
  <prefix>_prs_histogram.png   — overlapping histograms per group (or single if no groups)
  <prefix>_prs_boxplot.png     — boxplot per group (only when 2+ phenotype groups present)

prefix defaults to "prs" when --prefix is not supplied.
"""

import argparse
import os
import sys

import pandas as pd
import matplotlib
matplotlib.use("Agg")   # non-interactive backend; must be set before importing pyplot
import matplotlib.pyplot as plt

_PHENO_COLS   = ["PHENO", "pheno", "phenotype", "PHENOTYPE"]
_PLINK_LABELS = {1: "control", 2: "case", 1.0: "control", 2.0: "case"}
_COLOURS      = {"control": "#4393C3", "case": "#D6604D"}
_FALLBACK_COLOURS = [
    "#4393C3", "#D6604D", "#74C476", "#FD8D3C", "#9E9AC8", "#FDAE6B",
]


def _find_col(df: pd.DataFrame, candidates: list) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None


def _group_colour(label: str, idx: int) -> str:
    return _COLOURS.get(label, _FALLBACK_COLOURS[idx % len(_FALLBACK_COLOURS)])


def main():
    parser = argparse.ArgumentParser(description="Plot PRS distribution")
    parser.add_argument("--merged",  required=True,
                        help="Merged PRS + phenotype TSV (output of merge_prs_pheno.py)")
    parser.add_argument("--out-dir", required=True,
                        help="Directory to write output figures")
    parser.add_argument("--prefix", default="prs",
                        help="Filename prefix for output figures (default: 'prs')")
    args = parser.parse_args()

    os.makedirs(args.out_dir, exist_ok=True)

    df = pd.read_csv(args.merged, sep="\t")
    if "PRS" not in df.columns:
        sys.exit("Error: 'PRS' column not found in merged file. "
                 "Check that merge_prs_pheno.py ran successfully.")

    # Determine grouping
    pheno_col = _find_col(df, _PHENO_COLS)
    if pheno_col:
        unique_vals = set(df[pheno_col].dropna().unique())
        if unique_vals.issubset({1, 2, 1.0, 2.0}):
            df["_group"] = df[pheno_col].map(_PLINK_LABELS)
        else:
            df["_group"] = df[pheno_col].astype(str)
    else:
        df["_group"] = "all"

    groups = sorted(df["_group"].dropna().unique())

    # ---- Histogram ----
    fig, ax = plt.subplots(figsize=(7, 4))
    for idx, g in enumerate(groups):
        subset = df.loc[df["_group"] == g, "PRS"].dropna()
        ax.hist(
            subset,
            bins=20,
            alpha=0.6,
            label=g,
            color=_group_colour(g, idx),
            edgecolor="white",
            linewidth=0.4,
        )
    ax.set_xlabel("Polygenic Risk Score", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    ax.set_title("PRS Distribution — Demo Asthma Dataset", fontsize=13)
    if len(groups) > 1:
        ax.legend(title="Group", frameon=False, fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()

    hist_path = os.path.join(args.out_dir, f"{args.prefix}_prs_histogram.png")
    fig.savefig(hist_path, dpi=150)
    plt.close(fig)
    print(f"Histogram saved:  {hist_path}")

    # ---- Boxplot (only when 2+ groups exist) ----
    if len(groups) < 2:
        print("Single group — skipping boxplot.")
        return

    data_by_group = [df.loc[df["_group"] == g, "PRS"].dropna().values for g in groups]
    colours       = [_group_colour(g, i) for i, g in enumerate(groups)]

    fig, ax = plt.subplots(figsize=(4 + len(groups), 4))
    bp = ax.boxplot(
        data_by_group,
        patch_artist=True,
        labels=groups,
        widths=0.5,
        medianprops=dict(color="black", linewidth=2),
        flierprops=dict(marker="o", markersize=3, alpha=0.5),
    )
    for patch, colour in zip(bp["boxes"], colours):
        patch.set_facecolor(colour)
        patch.set_alpha(0.7)

    ax.set_xlabel("Group", fontsize=12)
    ax.set_ylabel("Polygenic Risk Score", fontsize=12)
    ax.set_title("PRS by Phenotype Group — Demo", fontsize=13)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()

    box_path = os.path.join(args.out_dir, f"{args.prefix}_prs_boxplot.png")
    fig.savefig(box_path, dpi=150)
    plt.close(fig)
    print(f"Boxplot saved:    {box_path}")


if __name__ == "__main__":
    main()

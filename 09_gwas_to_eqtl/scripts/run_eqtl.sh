#!/bin/bash
set -euo pipefail

# End-to-end GWAS-to-eQTL annotation workflow:
#   Step 1  extract_top_gwas_hits.py   extract top variants from GWAS results
#   Step 2  map_gwas_to_eqtl.py        annotate hits with eQTL reference
#   Step 3  plot_gwas_eqtl_summary.py  generate summary figure
#
# Usage:
#   bash scripts/run_eqtl.sh <GWAS_FILE> <EQTL_REF> <OUT_PREFIX> [TOP_N]
#
# Arguments:
#   GWAS_FILE    PLINK .assoc.logistic file (CHR SNP BP A1 TEST NMISS OR STAT P)
#   EQTL_REF     eQTL reference TSV (SNP, eQTL_gene, tissue, eqtl_beta, source)
#   OUT_PREFIX   Output prefix; all result files are written as <OUT_PREFIX>_*
#   TOP_N        Optional. Number of top GWAS hits to retain (default: 20)
#
# Example:
#   cd 09_gwas_to_eqtl
#   bash scripts/run_eqtl.sh \
#     ../06_asthma_gwas/results/asthma_gwas.assoc.logistic \
#     data/demo_eqtl_reference.tsv \
#     results/eqtl_annotation

# ---- Working directory guard ----
if [[ ! -f "scripts/run_eqtl.sh" ]]; then
    echo "Error: run this script from the 09_gwas_to_eqtl/ directory."
    echo "  cd 09_gwas_to_eqtl && bash scripts/run_eqtl.sh ..."
    exit 1
fi

# ---- Argument check ----
if [[ $# -lt 3 ]] || [[ $# -gt 4 ]]; then
    echo "Usage: bash scripts/run_eqtl.sh <GWAS_FILE> <EQTL_REF> <OUT_PREFIX> [TOP_N]"
    echo ""
    echo "  GWAS_FILE    PLINK .assoc.logistic file"
    echo "  EQTL_REF     eQTL reference TSV"
    echo "  OUT_PREFIX   Output prefix for all generated files"
    echo "  TOP_N        Number of top variants to retain (default: 20)"
    echo ""
    echo "Example:"
    echo "  bash scripts/run_eqtl.sh \\"
    echo "    ../06_asthma_gwas/results/asthma_gwas.assoc.logistic \\"
    echo "    data/demo_eqtl_reference.tsv \\"
    echo "    results/eqtl_annotation"
    exit 1
fi

GWAS_FILE="$1"
EQTL_REF="$2"
OUT_PREFIX="$3"
TOP_N="${4:-20}"

# ---- Input validation ----
if [[ ! -f "$GWAS_FILE" ]]; then
    echo "Error: GWAS file not found: $GWAS_FILE"
    exit 1
fi

if [[ ! -f "$EQTL_REF" ]]; then
    echo "Error: eQTL reference file not found: $EQTL_REF"
    exit 1
fi

# ---- Create output directories ----
OUT_DIR=$(dirname "$OUT_PREFIX")
FIGURES_DIR="${OUT_DIR}/figures"
mkdir -p "$OUT_DIR" "$FIGURES_DIR"

# Derived file paths
HITS_FILE="${OUT_PREFIX}_hits.tsv"
FIGURE_PREFIX="$(basename "$OUT_PREFIX")"

echo "=== GWAS-to-eQTL Workflow ==="
echo "  GWAS file  : $GWAS_FILE"
echo "  eQTL ref   : $EQTL_REF"
echo "  Output     : $OUT_PREFIX"
echo "  Top N      : $TOP_N"
echo ""

# ---- Step 1: Extract top GWAS hits ----
echo "Step 1: Extracting top GWAS hits..."
python scripts/extract_top_gwas_hits.py \
    --gwas   "$GWAS_FILE" \
    --out    "$HITS_FILE" \
    --top-n  "$TOP_N"
echo "  -> $HITS_FILE"
echo ""

# ---- Step 2: Annotate with eQTL reference ----
echo "Step 2: Mapping GWAS hits to eQTL reference..."
python scripts/map_gwas_to_eqtl.py \
    --gwas-hits  "$HITS_FILE" \
    --eqtl-ref   "$EQTL_REF" \
    --out        "$OUT_PREFIX"
echo "  -> ${OUT_PREFIX}_candidates.tsv"
echo "  -> ${OUT_PREFIX}_prioritized.tsv"
echo ""

# ---- Step 3: Plot ----
echo "Step 3: Generating summary figure..."
python scripts/plot_gwas_eqtl_summary.py \
    --candidates "${OUT_PREFIX}_candidates.tsv" \
    --out-dir    "$FIGURES_DIR" \
    --prefix     "$FIGURE_PREFIX"
echo ""

echo "=== Done ==="
echo "Outputs:"
echo "  $HITS_FILE"
echo "  ${OUT_PREFIX}_candidates.tsv"
echo "  ${OUT_PREFIX}_prioritized.tsv"
echo "  ${FIGURES_DIR}/${FIGURE_PREFIX}_gwas_eqtl_summary.png"

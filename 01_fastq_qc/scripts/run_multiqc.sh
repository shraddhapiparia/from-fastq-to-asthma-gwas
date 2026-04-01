#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 <FASTQC_DIR> <OUTDIR>

Example:
  $0 results/fastqc results/multiqc

Notes:
- FASTQC_DIR should contain FastQC HTML/zip outputs. MultiQC will scan the directory recursively.
EOF
}

if [[ "$#" -ne 2 ]]; then
  usage
  exit 1
fi

FASTQC_DIR="$1"
OUTDIR="$2"

command -v multiqc >/dev/null 2>&1 || { echo "multiqc not found in PATH" >&2; exit 1; }

mkdir -p "$OUTDIR"

echo "Running MultiQC on $FASTQC_DIR -> $OUTDIR"
multiqc -o "$OUTDIR" "$FASTQC_DIR"

echo "MultiQC finished. Report is $OUTDIR/multiqc_report.html"

#!/usr/bin/env bash
set -euo pipefail

usage(){
  cat <<EOF
Usage: $0 <IN_VCF_GZ> <OUT_VCF_GZ>

Example:
  $0 results/sample.vcf.gz results/sample_filtered.vcf.gz
EOF
}

if [[ "$#" -ne 2 ]]; then
  usage
  exit 1
fi

IN_VCF_GZ="$1"
OUT_VCF_GZ="$2"

command -v bcftools >/dev/null 2>&1 || { echo "bcftools not found" >&2; exit 1; }

mkdir -p "$(dirname "$OUT_VCF_GZ")"

echo "Filtering variants: $IN_VCF_GZ -> $OUT_VCF_GZ"

# Basic filtering: quality >= 20
bcftools filter -i 'QUAL>=20' "$IN_VCF_GZ" \
  | bcftools view -Oz -o "$OUT_VCF_GZ"

bcftools index "$OUT_VCF_GZ"

echo "Filtering finished. Filtered VCF: $OUT_VCF_GZ"
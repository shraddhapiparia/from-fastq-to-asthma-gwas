#!/usr/bin/env bash
set -euo pipefail

usage(){
  cat <<EOF
Usage: $0 <REFERENCE_FA> <BAM> <OUT_VCF_GZ>

Example:
  $0 refs/toy_reference.fa results/sample.bam results/sample.vcf.gz
EOF
}

if [[ "$#" -ne 3 ]]; then
  usage
  exit 1
fi

REF="$1"
BAM="$2"
OUT_VCF_GZ="$3"

command -v gatk >/dev/null 2>&1 || { echo "gatk not found" >&2; exit 1; }
command -v bcftools >/dev/null 2>&1 || { echo "bcftools not found" >&2; exit 1; }

mkdir -p "$(dirname "$OUT_VCF_GZ")"

echo "Running GATK HaplotypeCaller on $BAM -> $OUT_VCF_GZ"

gatk HaplotypeCaller \
  -R "$REF" \
  -I "$BAM" \
  -O "$OUT_VCF_GZ" \
  --min-base-quality-score 20 \
  --standard-min-confidence-threshold-for-calling 20

echo "HaplotypeCaller finished. VCF: $OUT_VCF_GZ"
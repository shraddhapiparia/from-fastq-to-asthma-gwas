#!/usr/bin/env bash
set -euo pipefail

usage(){
  cat <<EOF
Usage: $0 <IN_VCF_GZ> <OUT_SUMMARY>

Example:
  $0 results/HG002_chr20_10_20Mb.filtered.vcf.gz results/annotated_summary.txt
EOF
}

if [[ "$#" -ne 2 ]]; then
  usage
  exit 1
fi

IN_VCF_GZ="$1"
OUT_SUMMARY="$2"

command -v bcftools >/dev/null 2>&1 || {
  echo "bcftools not found" >&2
  exit 1
}

mkdir -p "$(dirname "$OUT_SUMMARY")"

TOTAL=$(bcftools view -H "$IN_VCF_GZ" | wc -l)
SNPS=$(bcftools view -H -v snps "$IN_VCF_GZ" | wc -l)
INDELS=$(bcftools view -H -v indels "$IN_VCF_GZ" | wc -l)

{
  echo "Variant Summary"
  echo "==============="
  echo "Input VCF: $IN_VCF_GZ"
  echo "Total variants: $TOTAL"
  echo "SNPs: $SNPS"
  echo "Indels: $INDELS"
  echo ""
  echo "Example variants:"
  echo -e "CHROM\tPOS\tREF\tALT\tQUAL\tINFO_DP"
  bcftools query \
    -f '%CHROM\t%POS\t%REF\t%ALT\t%QUAL\t%INFO/DP\n' \
    "$IN_VCF_GZ" | head -10
} > "$OUT_SUMMARY"

echo "Annotation finished. Summary written to: $OUT_SUMMARY"
#!/usr/bin/env bash
set -euo pipefail

usage(){
  cat <<EOF
Usage: $0 <IN_BAM> <OUT_DIR> [-t THREADS]

Example:
  $0 results/sample_unsorted.bam results/processed -t 4
EOF
}

if [[ "$#" -lt 2 ]]; then
  usage
  exit 1
fi

IN_BAM="$1"
OUT_DIR="$2"
shift 2
THREADS=1
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    -t) THREADS="$2"; shift 2;;
    *) shift;;
  esac
done

command -v samtools >/dev/null 2>&1 || { echo "samtools not found" >&2; exit 1; }
command -v picard >/dev/null 2>&1 || { echo "picard not found" >&2; exit 1; }

mkdir -p "$OUT_DIR"

BASE="$(basename "$IN_BAM" .bam)"
SORTED_BAM="$OUT_DIR/${BASE}.sorted.bam"
DEDUP_BAM="$OUT_DIR/${BASE}.dedup.bam"
METRICS="$OUT_DIR/${BASE}.metrics.txt"
FLAGSTAT="$OUT_DIR/${BASE}.flagstat.txt"

echo "Sorting BAM -> $SORTED_BAM"
samtools sort -@ "$THREADS" -o "$SORTED_BAM" "$IN_BAM"

echo "Indexing sorted BAM"
samtools index "$SORTED_BAM"

echo "Marking duplicates (Picard) -> $DEDUP_BAM"
picard MarkDuplicates I="$SORTED_BAM" O="$DEDUP_BAM" M="$METRICS" CREATE_INDEX=true

echo "Generating flagstat -> $FLAGSTAT"
samtools flagstat "$DEDUP_BAM" > "$FLAGSTAT"

echo "Processing complete. Outputs in: $OUT_DIR"

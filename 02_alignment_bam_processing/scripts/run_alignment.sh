#!/usr/bin/env bash
set -euo pipefail

usage(){
  cat <<EOF
Usage: $0 <REFERENCE_FA> <FASTQ_R1[.gz]> <OUT_BAM> [-t THREADS]

Example:
  $0 refs/chr20.fa data/NA12878_small_R1.fastq.gz results/sample_unsorted.bam -t 4
EOF
}

if [[ "$#" -lt 3 ]]; then
  usage
  exit 1
fi

REF="$1"
FASTQ="$2"
OUT_BAM="$3"
shift 3
THREADS=1
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    -t) THREADS="$2"; shift 2;;
    *) shift;;
  esac
done

command -v bwa >/dev/null 2>&1 || { echo "bwa not found" >&2; exit 1; }
command -v samtools >/dev/null 2>&1 || { echo "samtools not found" >&2; exit 1; }

mkdir -p "$(dirname "$OUT_BAM")"

echo "Running bwa mem -> SAM -> BAM (unsorted)"

# Run bwa mem, pipe to samtools view to produce BAM
bwa mem -t "$THREADS" "$REF" "$FASTQ" | samtools view -bS - > "$OUT_BAM"

echo "Wrote unsorted BAM: $OUT_BAM"

#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<EOF
Usage: $0 [FASTQ ...] <OUTDIR> [-t THREADS]

Example:
  $0 NA12878_small_R1.fastq.gz results/fastqc -t 4

Notes:
- Provide one or more FASTQ files followed by an output directory.
- Optional flag '-t THREADS' (anywhere in args) sets FastQC threads.
EOF
}

if [[ "$#" -lt 2 ]]; then
  usage
  exit 1
fi

# Gather args and optional -t
ARGS=("$@")
THREADS=1
for i in "${!ARGS[@]}"; do
  if [[ "${ARGS[$i]}" == "-t" ]]; then
    THREADS="${ARGS[$i+1]:-1}"
    unset 'ARGS[$i]'
    unset 'ARGS[$i+1]'
    ARGS=("${ARGS[@]}")
    break
  fi
done

# Last argument is the output directory
NARGS=${#ARGS[@]}
if [[ $NARGS -lt 2 ]]; then
  usage
  exit 1
fi
OUTDIR="${ARGS[$NARGS-1]}"
FILES=("${ARGS[@]:0:$NARGS-1}")

command -v fastqc >/dev/null 2>&1 || { echo "fastqc not found in PATH" >&2; exit 1; }

mkdir -p "$OUTDIR"

echo "Running FastQC on ${#FILES[@]} file(s) -> $OUTDIR (threads=$THREADS)"
fastqc -o "$OUTDIR" -t "$THREADS" "${FILES[@]}"

echo "FastQC finished. HTML reports and zips are in: $OUTDIR"

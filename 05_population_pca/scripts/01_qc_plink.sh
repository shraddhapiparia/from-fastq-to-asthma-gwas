#!/bin/bash
set -euo pipefail

# Basic genotype QC for demo purposes
# Input: ../datasets/data/demo_genotypes.{bed,bim,fam}
# Output: results/demo_genotypes_qc.{bed,bim,fam}

echo "Running basic genotype QC..."

# For demo purposes, we use lenient QC thresholds
# Real studies would use stricter filters (e.g., MAF > 0.05, missing < 0.05)

# Filters: MAF > 1%, genotype missingness < 10%, sample missingness < 10%, HWE p > 1e-6
plink \
    --bfile ../datasets/data/demo_genotypes \
    --maf 0.01 \
    --geno 0.1 \
    --mind 0.1 \
    --hwe 1e-6 \
    --make-bed \
    --out results/demo_genotypes_qc

SNPS=$(wc -l < results/demo_genotypes_qc.bim)
SAMPLES=$(wc -l < results/demo_genotypes_qc.fam)
echo "QC complete. Retained ${SNPS} SNPs and ${SAMPLES} samples."
printf "stage\tsnps\tsamples\n" > results/qc_summary.txt
printf "post_qc\t%s\t%s\n" "${SNPS}" "${SAMPLES}" >> results/qc_summary.txt
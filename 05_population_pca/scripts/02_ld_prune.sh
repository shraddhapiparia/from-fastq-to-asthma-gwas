#!/bin/bash
set -euo pipefail

# LD pruning before PCA to reduce redundancy
# Input: results/demo_genotypes_qc.{bed,bim,fam}
# Output: results/demo_genotypes_pruned.{bed,bim,fam}

echo "Running LD pruning..."

# LD pruning parameters: 50kb window, 5kb step, r² > 0.2
# This removes SNPs in high LD to avoid over-representing regions in PCA

plink \
    --bfile results/demo_genotypes_qc \
    --indep-pairwise 50 5 0.2 \
    --out results/demo_genotypes_pruned

# Extract pruned SNPs
plink \
    --bfile results/demo_genotypes_qc \
    --extract results/demo_genotypes_pruned.prune.in \
    --make-bed \
    --out results/demo_genotypes_pruned

echo "LD pruning complete. Retained $(wc -l < results/demo_genotypes_pruned.bim) SNPs."
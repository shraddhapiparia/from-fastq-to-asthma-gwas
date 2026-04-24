#!/bin/bash
set -euo pipefail

# Run PCA on pruned dataset
# Input: results/demo_genotypes_pruned.{bed,bim,fam}
# Output: results/demo_genotypes_pca.{eigenvec,eigenval}

echo "Running PCA..."

# Compute first 10 principal components
plink \
    --bfile results/demo_genotypes_pruned \
    --pca 10 \
    --out results/demo_genotypes_pca

echo "PCA complete. Eigenvalues: $(head -5 results/demo_genotypes_pca.eigenval)"
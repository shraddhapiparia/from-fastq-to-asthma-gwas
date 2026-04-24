#!/bin/bash
set -euo pipefail

# Run GWAS with logistic regression
# Input: ../05_population_pca/results/demo_genotypes_qc.{bed,bim,fam}
#        results/asthma_pheno.txt
#        ../05_population_pca/results/demo_genotypes_pca.eigenvec
# Output: results/asthma_gwas.assoc.logistic

echo "Running GWAS..."

# Create covariate file from PCA (PC1-PC5)
# awk field-split handles any whitespace in eigenvec (more robust than cut -d' ')
echo "FID IID PC1 PC2 PC3 PC4 PC5" > results/pca_covariates.txt
awk '{print $1, $2, $3, $4, $5, $6, $7}' \
    ../05_population_pca/results/demo_genotypes_pca.eigenvec >> results/pca_covariates.txt

# Run logistic regression GWAS
# --hide-covar: omit per-covariate rows from output (R script filters ADD anyway)
# --allow-no-sex: suppress warnings from --dummy data which has no sex phenotype
plink \
    --bfile ../05_population_pca/results/demo_genotypes_qc \
    --pheno results/asthma_pheno.txt \
    --covar results/pca_covariates.txt \
    --logistic hide-covar \
    --allow-no-sex \
    --out results/asthma_gwas

echo "GWAS complete. Results saved to results/asthma_gwas.assoc.logistic"
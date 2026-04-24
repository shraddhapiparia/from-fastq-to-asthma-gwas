#!/bin/bash
set -euo pipefail

# Simulate a small demo genotype dataset for educational purposes
# Creates 100 samples with 1000 SNPs using PLINK's dummy data generator

echo "Simulating demo genotype dataset..."

# Create dummy data: 100 samples, 1000 SNPs
plink --dummy 100 1000 --out data/demo_genotypes

# Add population labels to fam file for PCA demonstration
# Simulate 3 populations: EUR, AFR, EAS
awk 'BEGIN {srand(42)}
NR >= 1 {
    pop = "EUR"
    if (NR % 3 == 0) pop = "AFR"
    else if (NR % 3 == 1) pop = "EAS"
    print $1, $2, $3, $4, $5, $6, pop
}' data/demo_genotypes.fam > data/demo_genotypes.fam.tmp && mv data/demo_genotypes.fam.tmp data/demo_genotypes.fam

echo "Demo dataset created in data/demo_genotypes.{bed,bim,fam}"
echo "Population labels added to fam file for demonstration"
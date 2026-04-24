#!/bin/bash
set -euo pipefail

# Wrapper script for toy asthma GWAS workflow
# Usage: bash scripts/run_gwas.sh

echo "Starting toy asthma GWAS workflow..."

# Must be run from the 06_asthma_gwas/ directory
if [[ ! -f "scripts/run_gwas.sh" ]]; then
    echo "Error: run this script from the 06_asthma_gwas/ directory."
    echo "  cd 06_asthma_gwas && bash scripts/run_gwas.sh"
    exit 1
fi

# Check for Stage 05 outputs
if [[ ! -f "../05_population_pca/results/demo_genotypes_qc.bed" ]]; then
    echo "Error: QC genotype data not found. Run module 05 first."
    exit 1
fi

if [[ ! -f "../05_population_pca/results/demo_genotypes_pca.eigenvec" ]]; then
    echo "Error: PCA eigenvec not found. Run module 05 first."
    exit 1
fi

# Step 1: Prepare phenotype
echo "Step 1: Preparing simulated phenotype..."
python scripts/01_prepare_pheno.py

# Step 2: Run GWAS
echo "Step 2: Running GWAS..."
bash scripts/02_run_gwas.sh

# Step 3: Plot results
echo "Step 3: Generating plots..."
Rscript scripts/03_plot_manhattan_qq.R

echo "GWAS workflow complete. Check results/ and figures/ for outputs."
#!/bin/bash
set -euo pipefail

# Wrapper script for genotype QC and PCA workflow
# Usage: bash scripts/run_qc_pca.sh

echo "Starting genotype QC and PCA workflow..."

# Must be run from the 05_population_pca/ directory
if [[ ! -f "scripts/run_qc_pca.sh" ]]; then
    echo "Error: run this script from the 05_population_pca/ directory."
    echo "  cd 05_population_pca && bash scripts/run_qc_pca.sh"
    exit 1
fi

# Check for input data
if [[ ! -f "../datasets/data/demo_genotypes.bed" ]]; then
    echo "Error: Demo genotype data not found. Run '../datasets/scripts/simulate_demo_data.sh' first."
    exit 1
fi

# Step 1: QC
echo "Step 1: Running QC..."
bash scripts/01_qc_plink.sh

# Step 2: LD pruning
echo "Step 2: LD pruning..."
bash scripts/02_ld_prune.sh

# Step 3: PCA
echo "Step 3: Running PCA..."
bash scripts/03_run_pca.sh

# Step 4: Plotting
echo "Step 4: Generating PCA plot..."
Rscript scripts/04_plot_pca.R

echo "Workflow complete. Check results/ and figures/ for outputs."
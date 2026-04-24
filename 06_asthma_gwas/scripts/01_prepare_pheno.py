#!/usr/bin/env python3

# Prepare simulated asthma phenotype for demo GWAS
# Creates a binary phenotype with weak correlation to ancestry (PC1)

import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Read PCA results from module 05 — eigenvec is space-delimited (not tab)
pca_file = "../05_population_pca/results/demo_genotypes_pca.eigenvec"
pca = pd.read_csv(pca_file, sep=r'\s+', engine='python', header=None,
                  names=['FID', 'IID'] + [f'PC{i}' for i in range(1, 11)])

# Simulate phenotype: 20% cases, with weak effect of PC1
n_samples = len(pca)
prob_case = 0.2 + 0.1 * pca['PC1']  # Weak correlation with ancestry
prob_case = np.clip(prob_case, 0.1, 0.9)  # Keep probabilities reasonable

phenotype_01 = np.random.binomial(1, prob_case, n_samples)
# PLINK logistic expects 1=control, 2=case (0 is treated as missing)
phenotype = phenotype_01 + 1

# Create phenotype file (PLINK format: FID IID PHENO)
pheno_df = pd.DataFrame({
    'FID': pca['FID'],
    'IID': pca['IID'],
    'PHENO': phenotype
})

pheno_df.to_csv('results/asthma_pheno.txt', sep='\t', index=False)

n_cases = (phenotype == 2).sum()
print(f"Simulated phenotype created for {n_samples} samples")
print(f"Cases (PHENO=2): {n_cases}  Controls (PHENO=1): {n_samples - n_cases}")
print("Phenotype saved to results/asthma_pheno.txt")
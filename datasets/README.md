# Datasets

This directory contains shared input data documentation and scripts for generating demo datasets used across multiple projects.

## Demo Genotype Dataset

For projects 05-09, we use a small simulated genotype dataset to demonstrate genotype-based analyses without requiring large downloads.

### Generating the Demo Dataset

Run the following to create a small PLINK dataset with 100 samples and 1000 SNPs:

```bash
cd datasets
conda env create -f ../envs/genomics_pipeline.yml
conda activate genomics_pipeline
bash scripts/simulate_demo_data.sh
```

This creates `data/demo_genotypes.{bed,bim,fam}` files.

### Dataset Details

- **Samples**: 100 simulated individuals
- **SNPs**: 1000 biallelic SNPs on chromosome 1
- **Format**: PLINK binary (.bed/.bim/.fam)
- **Purpose**: Educational demonstration only, not biologically meaningful

The dataset is generated using PLINK's --dummy option for testing purposes. Population labels are added manually for PCA demonstration.

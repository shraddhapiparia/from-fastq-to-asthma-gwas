# From FASTQ to Asthma GWAS

An end-to-end genomics pipeline demonstrating how raw DNA sequencing data are transformed into biological insight: from FASTQ files to GWAS signals, polygenic risk scores, and gene-level interpretation in asthma.

This repository is designed as a practical, reproducible portfolio project that reflects how genomic data are processed and analyzed in real research settings.

---

## What This Project Demonstrates

This project answers a central question in human genetics:

**How do we go from raw sequencing data to understanding genetic risk for disease?**

The workflow covers:

- Sequencing quality control and data validation  
- Read alignment and BAM processing  
- Variant discovery and filtering  
- Variant annotation and biological interpretation  
- Population structure analysis (PCA)  
- Genome-wide association study (GWAS)  
- Polygenic risk score (PRS) construction  
- Functional interpretation via GWAS → eQTL mapping  

While the pipeline is general, later stages focus on asthma genetics to demonstrate how computational results connect to disease biology.

---

## End-to-End Workflow

FASTQ  
↓  
Quality Control (FastQC, MultiQC)  
↓  
Alignment (BWA)  
↓  
BAM Processing (Samtools, Picard)  
↓  
Variant Calling (GATK)  
↓  
Variant Annotation  
↓  
Population Structure (PCA)  
↓  
GWAS  
↓  
Polygenic Risk Score (PRS)  
↓  
GWAS → eQTL Interpretation  

---

## Repository Structure

from-fastq-to-asthma-gwas/  
├── datasets/  
├── 01_fastq_qc/  
├── 02_alignment_bam_processing/  
├── 03_variant_calling_gatk/  
├── 04_variant_annotation/  
├── 05_population_pca/  
├── 06_asthma_gwas/  
├── 07_polygenic_risk_score/  
├── 08_rare_variant_testing/  
├── 09_gwas_to_eqtl/  
├── 10_nextflow_pipeline/  

---

## Modules Overview

| Module | What It Does | Why It Matters |
|--------|-------------|----------------|
| 01_fastq_qc | Evaluates sequencing quality | Detects issues before downstream analysis |
| 02_alignment_bam_processing | Maps reads to reference genome | Converts raw reads into genomic coordinates |
| 03_variant_calling_gatk | Identifies SNPs and indels | Core step for detecting genetic variation |
| 04_variant_annotation | Adds gene-level interpretation | Connects variants to biology |
| 05_population_pca | Computes ancestry structure | Controls confounding in GWAS |
| 06_asthma_gwas | Identifies associated variants | Links genotype to phenotype |
| 07_polygenic_risk_score | Builds polygenic risk score | Aggregates genetic risk across variants |
| 08_rare_variant_testing | Gene-level burden testing | Captures effects of rare variants |
| 09_gwas_to_eqtl | Maps variants to gene expression | Generates mechanistic hypotheses |
| 10_nextflow_pipeline | Reproducible pipeline | Scales workflow to production settings |

---

## Key Concepts

This project focuses on core concepts that drive most genomics workflows:

- Why sequencing QC determines downstream success  
- How alignment quality impacts variant calling  
- How false positives arise in variant detection  
- Why population stratification biases GWAS  
- How GWAS signals map to biological mechanisms  
- Why PRS requires careful interpretation (not diagnostic)  

---

## 🧬 Example Biological Interpretation (Asthma)

Later modules demonstrate how computational outputs translate into biological hypotheses.

Example:

- GWAS identifies variants associated with asthma risk  
- These variants map to loci near genes such as:
  - ORMDL3 / GSDMB  
  - IL1RL1  
  - IL13  
  - FCER1A  
- eQTL mapping suggests these variants may influence gene expression in lung or immune tissues  

This reflects a typical reasoning path in genomics:

Variant → Gene → Expression → Disease Mechanism

---

## Datasets

To keep the project lightweight and reproducible:

- Genome in a Bottle (HG002 / NA12878)  
  Used for sequencing, alignment, and variant calling modules  

- Simulated / subset genotype datasets  
  Used for PCA, GWAS, and PRS modules  

- GTEx (reference-based)  
  Used for GWAS → eQTL interpretation  

---

## Important Notes

- This is a demonstration-scale pipeline, not a production GWAS  
- Some modules use simulated or subset data for speed  
- Results are for workflow demonstration, not biological claims  

---

## How to Run

Each module is self-contained with its own environment and scripts.

Example:

```bash
cd 05_population_pca
conda env create -f environment.yml
conda activate population_pca_env
bash scripts/run_qc_pca.sh
```

See individual module READMEs for full instructions.

---

## What This Shows

This repository demonstrates:

- Practical genomics pipeline implementation
- Reproducible workflow design
- Ability to connect computational outputs to biological interpretation

---

## Future Directions

This repository focuses on core DNA analysis workflows. More advanced extensions are being developed here or in parallel projects:

- RNA-seq and expression-based pipelines for downstream functional analysis  
- eQTL mapping from raw expression data and integration with GWAS signals  
- Fine-mapping and colocalization to identify likely causal variants  
- Multi-omic integration (genotype, expression, proteomics)  
- Machine learning approaches for genotype representation and polygenic risk modeling  

These directions reflect ongoing work in applying computational and statistical methods to understand disease mechanisms beyond standard GWAS pipelines. 

---

## Summary

This project demonstrates how genomics moves from:

raw sequencing data → statistical signals → biological insight

in a structured, reproducible, and interpretable way.

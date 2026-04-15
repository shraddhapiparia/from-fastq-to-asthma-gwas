# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a portfolio and educational genomics repository demonstrating the complete DNA analysis workflow — from raw FASTQ files through variant calling, GWAS, polygenic risk scores, and asthma-focused biological interpretation. Each numbered directory is a self-contained project.

**Core pipeline direction:**
```
FASTQ → QC → Alignment → BAM Processing → Variant Calling → Annotation → GWAS → PRS/eQTL
```

## Repository Structure

Each `NN_project_name/` directory is an independent, self-contained module. The `datasets/` directory holds shared input data documentation. Project 10 (`10_nextflow_pipeline`) wraps the full FASTQ-to-VCF workflow in Nextflow + Docker for reproducibility.

### Datasets

- **Projects 01–04, 10** (sequencing-based): NA12878 from Genome in a Bottle
- **Projects 05–09** (genotype-based): 1000 Genomes Project subset
- **Project 09** (functional): GTEx (lung/blood tissue expression)

## Project Modules

| Dir | Purpose | Key Tools |
|-----|---------|-----------|
| `01_fastq_qc` | Sequencing quality + adapter trimming | FastQC, MultiQC |
| `02_alignment_bam_processing` | Read alignment + BAM processing | BWA, Samtools, Picard |
| `03_variant_calling_gatk` | SNP/indel calling | GATK, bcftools |
| `04_variant_annotation` | Gene names + predicted consequences | VEP, SnpEff, ClinVar |
| `05_population_pca` | Genotype QC + ancestry PCA | PLINK |
| `06_asthma_gwas` | GWAS + Manhattan/QQ plots | PLINK, R |
| `07_polygenic_risk_score` | Asthma PRS computation | PRSice, PLINK |
| `08_rare_variant_testing` | Gene-based burden testing | SKAT, RVTests |
| `09_gwas_to_eqtl` | GWAS SNP → gene expression via GTEx | GTEx, Ensembl |
| `10_nextflow_pipeline` | Reproducible FASTQ-to-VCF workflow | Nextflow, Docker |

## Asthma Biology Context

Later projects frame results around asthma-relevant genes: **ORMDL3/GSDMB**, **IL1RL1**, **IL13**, **FCER1A**, **IL18R1**. The goal is to demonstrate how a genomics scientist moves from raw data to a biologically meaningful question — not to make strong claims from small public datasets.

## Development Status

This repository is in active construction. As projects are implemented, each directory will typically contain:
- A shell script or Snakemake/Nextflow workflow
- R or Python scripts for analysis and plotting
- A per-project README explaining inputs, outputs, and interpretation

## Working Principles

- Do not fake expertise. If a task requires domain-specific validation that cannot be performed from the repository alone, say so clearly and offer to write code, suggest checks, or point to the right tools.

- Do not assert runtime behavior, performance, output values, or biological conclusions unless they have been verified. If something can be tested by running code, inspecting logs, or checking files, do that first.

- Push back on incorrect assumptions instead of building on top of them. If an input, method, interpretation, or biological claim appears wrong or unsupported, explain why and suggest a better approach.

- State uncertainty explicitly. Prefer phrases like "I think", "I am not sure", "this likely means", or "this should be verified" over confident but unsupported claims.

- Ask for context before giving open-ended advice. For example:
  - user's background
  - project goals
  - available data
  - compute constraints
  - whether this is for learning, publication, or production

- Prefer reproducibility over speculation:
  - show exact commands
  - reference file names and expected outputs
  - explain assumptions
  - keep recommendations grounded in the repository structure

- Avoid overclaiming from small public datasets. This repository is educational and portfolio-oriented. Results should be framed as demonstrations of workflow and interpretation, not strong biological conclusions.

- Do not use em dashes. Use commas, colons, semicolons, or separate sentences instead.

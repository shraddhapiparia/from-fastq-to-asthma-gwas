# From FASTQ to Asthma GWAS

Small, practical genomics projects that demonstrate the core DNA analysis workflow used in human genetics research, from raw sequencing reads through variant calling, GWAS, polygenic risk scores, and asthma-focused biological interpretation.

This repository is intended as a portfolio and learning resource for understanding the tools commonly used by genomics scientists. Rather than focusing on a single large analysis, it contains a series of small, self-contained projects that together illustrate how DNA data move through a typical genomics pipeline.

The projects begin with raw sequencing data and gradually move toward increasingly biological questions:

- How do we assess sequencing quality?
- How are reads aligned to the reference genome?
- How are variants identified and interpreted?
- How do we analyze genotype data across individuals?
- How do we connect genetic variation to asthma risk and gene expression?

Although the technical workflow is general, later projects are framed around asthma-relevant genes and interpretation to reflect my broader research interests in asthma genetics, treatment response, and complex disease heterogeneity.

---

## Repository Structure

    from-fastq-to-asthma-gwas/
    ├── README.md
    ├── datasets/
    │   └── README.md
    ├── 01_fastq_qc/
    ├── 02_alignment_bam_processing/
    ├── 03_variant_calling_gatk/
    ├── 04_variant_annotation/
    ├── 05_population_pca/
    ├── 06_asthma_gwas/
    ├── 07_polygenic_risk_score/
    ├── 08_rare_variant_testing/
    ├── 09_gwas_to_eqtl/
    └── 10_nextflow_pipeline/

---

## Projects

| Project | Goal | Main Tools |
|----------|-------|-------------|
| `01_fastq_qc` | Assess sequencing quality and identify adapter contamination | FastQC, MultiQC |
| `02_alignment_bam_processing` | Align reads to the human reference genome and create a processed BAM file | BWA, Samtools, Picard |
| `03_variant_calling_gatk` | Call SNPs and indels from aligned sequencing data | GATK, bcftools |
| `04_variant_annotation` | Annotate variants with gene names and predicted consequences | VEP, SnpEff, ClinVar |
| `05_population_pca` | Perform genotype QC and ancestry PCA using population genotype data | PLINK |
| `06_asthma_gwas` | Run a small asthma-like GWAS and generate Manhattan and QQ plots | PLINK, R |
| `07_polygenic_risk_score` | Compute a simple asthma polygenic risk score | PRSice, PLINK |
| `08_rare_variant_testing` | Demonstrate gene-based burden testing using rare variants | SKAT, RVTests |
| `09_gwas_to_eqtl` | Connect a GWAS SNP to gene expression using GTEx | GTEx, Ensembl |
| `10_nextflow_pipeline` | Build a reproducible DNA analysis workflow from FASTQ to VCF | Nextflow, Docker |

---

## Workflow Overview

    FASTQ
      ↓
    Quality Control
      ↓
    Alignment
      ↓
    BAM Processing
      ↓
    Variant Calling
      ↓
    Variant Annotation
      ↓
    Population Structure / GWAS
      ↓
    PRS / Functional Interpretation

---

## Datasets Used

This repository uses small public datasets that are commonly used for practice and demonstration.

### Sequencing-Based Projects

The early projects use a small subset of the NA12878 sample from Genome in a Bottle, a standard benchmark dataset in genomics.

These projects include:

- FASTQ quality control
- Alignment and BAM processing
- Variant calling
- Variant annotation
- Nextflow pipeline

### Genotype-Based Projects

The later projects use a subset of the 1000 Genomes Project for population structure, GWAS, and polygenic risk score examples.

### Functional Interpretation

The GWAS follow-up project uses GTEx to investigate whether a top SNP is associated with gene expression in relevant tissues such as lung or blood.

---

## Asthma-Focused Interpretation

The early projects are intentionally general because the same sequencing and variant-calling tools are used across many diseases.

Later projects include asthma-focused interpretation by highlighting genes that are relevant to asthma susceptibility or treatment response, such as:

- ORMDL3 / GSDMB
- IL1RL1
- IL13
- FCER1A
- IL18R1

The goal is not to make strong biological claims from small public datasets, but rather to demonstrate how a genomics scientist might move from raw data to a biologically meaningful question.

For example:

- A variant may be annotated near an asthma-related gene
- A GWAS hit may be followed into GTEx to ask whether it changes expression in lung tissue
- A polygenic risk score may be computed using asthma GWAS summary statistics

---

## Why This Repository Exists

My recent work has focused on more advanced problems in computational genomics, including:

- GWAS and treatment-response modeling
- Asthma pharmacogenetics
- Genotype representation learning
- Polygenic risk scores
- Functional interpretation of genetic signals

This repository complements those projects by documenting the standard genomics workflow that underlies much of that work.

It is intended to show familiarity with the practical tools commonly used by genomics scientists while also connecting those tools to a disease area that motivates my research.

---

## Tools Covered

### Sequencing and Alignment

- FastQC
- MultiQC
- BWA
- Samtools
- Picard

### Variant Calling and Annotation

- GATK
- bcftools
- VEP
- SnpEff
- ClinVar

### Genotype Analysis

- PLINK
- PRSice
- SKAT
- RVTests

### Reproducibility

- Nextflow
- Docker

---

## Future Directions

Potential future additions include:

- RNA-seq workflow
- eQTL mapping from raw expression data
- Fine-mapping and credible sets
- Colocalization analysis
- Multi-omic interpretation of asthma-associated loci
- Integration with more advanced representation learning approaches

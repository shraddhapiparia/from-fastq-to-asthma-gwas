# 02: Alignment and BAM Processing

## Objective

Perform read alignment and BAM processing to convert raw sequencing reads into analysis-ready data for variant calling.

This step transforms FASTQ reads into genomic coordinates and prepares them for downstream analyses such as variant discovery.

---

## Why This Step Matters

Alignment is a critical step in genomics pipelines.

Errors at this stage directly affect:

- Mapping accuracy  
- Coverage estimates  
- Variant calling sensitivity and specificity  

Key risks include:

- Misaligned reads in repetitive regions  
- PCR duplicates inflating coverage  
- Poor mapping quality leading to false variants  

---

## Dataset

This module uses:

- A small FASTQ file from Project 01  
- A lightweight reference genome for fast execution  

The workflow mirrors real alignment pipelines while remaining computationally efficient.

---

## Tools

- `bwa` — read alignment  
- `samtools` — BAM processing and QC  
- `picard` — duplicate marking  
- `bash` — workflow scripts  

---

## Workflow Overview

1. Align reads to a reference genome  
2. Convert SAM to BAM  
3. Sort and index BAM  
4. Mark duplicate reads  
5. Generate alignment statistics  

---

## Running the Analysis

### Setup environment

```bash
conda activate genomics_pipeline
```

### Step 1: Index reference

```bash
cd 02_alignment_bam_processing
bwa index refs/toy_reference.fa
samtools faidx refs/toy_reference.fa
picard CreateSequenceDictionary R=refs/toy_reference.fa O=refs/toy_reference.dict
```

### Step 2: Create output directory

```bash
mkdir -p results/processed
```

### Step 3: Run alignment

```bash
bash scripts/run_alignment.sh refs/toy_reference.fa ../01_fastq_qc/data/NA12878_small_R1.fastq.gz results/sample_unsorted.bam -t 4
```

### Step 4: Process BAM

```bash
bash scripts/process_bam.sh results/sample_unsorted.bam results/processed -t 4
```

### Step 5: Inspect outputs

```bash
cat results/processed/sample_unsorted.flagstat.txt
head -20 results/processed/sample_unsorted.metrics.txt
```

---

## Expected Outputs

- `sample_unsorted.bam` — raw alignment output  
- `sample_unsorted.sorted.bam` — coordinate-sorted BAM  
- `sample_unsorted.sorted.bam.bai` — BAM index  
- `sample_unsorted.dedup.bam` — duplicate-marked BAM  
- `sample_unsorted.metrics.txt` — duplication statistics  
- `sample_unsorted.flagstat.txt` — alignment summary  

---

## How to Interpret Results

### Alignment rate

- High mapping rate (>90%) → good alignment  
- Low mapping rate → possible issues with reference, contamination, or read quality  

In this demonstration setup, low or zero mapping is expected due to mismatch between reads and reference.

---

### Duplicate rate

- Low duplication → good library complexity  
- High duplication (>20–30%) → potential PCR bias  

---

### Mapping quality

- High MAPQ → confident alignment  
- Low MAPQ → ambiguous or repetitive regions  

---

## Decision Guidelines

Based on alignment results:

- Good mapping and low duplication → proceed to variant calling  
- Low mapping rate → check reference genome or read quality  
- High duplication → consider filtering or reviewing library prep  
- Poor metrics overall → revisit QC step  

---

## What This Affects Downstream

Alignment quality directly impacts:

- Variant calling accuracy  
- False positive variant rates  
- Coverage-based analyses  

Poor alignment → unreliable variants  

---

## SAM vs BAM (Brief)

- SAM — human-readable alignment format  
- BAM — compressed binary format for efficient storage and processing  

---

## Why Sorting, Indexing, and Duplicate Marking?

- Sorting groups reads by genomic position for downstream tools  
- Indexing enables fast retrieval of genomic regions  
- Duplicate marking reduces bias in variant calling  

---

## Results

### Alignment workflow execution

The workflow completes successfully when all steps execute without error.

---

### Alignment statistics

The flagstat output summarizes:

- Total reads  
- Mapped reads  
- Duplicate reads  

---

## What This Module Demonstrates

- Reference indexing  
- Read alignment  
- SAM → BAM conversion  
- BAM sorting and indexing  
- Duplicate marking  
- Alignment quality assessment  

---

## Real-World Usage

In real sequencing projects:

- Reads are aligned to full reference genomes (e.g., GRCh38)  
- Multiple samples are processed in parallel  
- Alignment metrics are used for QC and filtering  
- High-quality BAM files are required for variant calling  

---

## Next Step

Proceed to:

**03_variant_calling_gatk**

to identify SNPs and indels from aligned sequencing data.
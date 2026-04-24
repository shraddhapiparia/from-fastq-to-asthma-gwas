# 03: Variant Calling with GATK

## Objective

Call SNPs and indels from aligned, processed BAM files using GATK HaplotypeCaller. Produce a filtered VCF ready for downstream annotation and association analysis.

---

## Why This Step Matters

Variant calling translates aligned reads into a discrete set of genetic differences relative to the reference genome. The accuracy of every downstream step — annotation, GWAS, PRS — depends directly on the quality of variants called here. GATK HaplotypeCaller is the industry-standard tool for germline short variant discovery because it performs local re-assembly of reads at candidate sites, which substantially reduces false positives compared to pileup-based callers.

---

## Dataset

- **Sample**: HG002 (Ashkenazi Jewish son) from the Genome in a Bottle (GIAB) consortium
- **Reference**: GRCh38 (hg38), subset to a small representative interval for reproducible demo runs
- **Input**: Duplicate-marked, base-quality-score-recalibrated BAM from module 02
- **Benchmark**: GIAB high-confidence variant calls for HG002 are available for precision/recall evaluation against this sample

---

## Tools

| Tool | Version | Purpose |
|------|---------|---------|
| GATK | 4.x | HaplotypeCaller, GenotypeGVCFs, VariantFiltration |
| bcftools | 1.x | Variant statistics, indexing, merging |
| samtools | 1.x | BAM indexing, sanity checks |

---

## Workflow Overview

```
BAM (module 02)
    ↓
HaplotypeCaller (GVCF mode)       — per-sample variant discovery with local re-assembly
    ↓
GenotypeGVCFs                     — produce final genotype calls from GVCF
    ↓
Hard filtering                    — apply SNP and indel filter expressions separately
    ↓
Filtered VCF                      → module 04 (variant annotation)
```

GVCF mode is used even for single samples to keep the workflow consistent with multi-sample joint genotyping pipelines.

---

## Running the Analysis

```bash
conda activate genomics_pipeline
cd 03_variant_calling_gatk
```

### Step 1 — Run HaplotypeCaller in GVCF mode

```bash
gatk HaplotypeCaller \
    -R data/ref/hg38_chr20_subset.fa \
    -I ../02_alignment_bam_processing/results/HG002.markdup.bqsr.bam \
    -O results/HG002.g.vcf.gz \
    -ERC GVCF \
    -L data/intervals/demo_interval.bed
```

### Step 2 — Genotype the GVCF

```bash
gatk GenotypeGVCFs \
    -R data/ref/hg38_chr20_subset.fa \
    -V results/HG002.g.vcf.gz \
    -O results/HG002.raw.vcf.gz \
    -L data/intervals/demo_interval.bed
```

### Step 3 — Apply hard filters

SNPs:

```bash
gatk VariantFiltration \
    -R data/ref/hg38_chr20_subset.fa \
    -V results/HG002.raw.vcf.gz \
    --select-type-to-include SNP \
    --filter-expression "QD < 2.0"               --filter-name "QD2" \
    --filter-expression "FS > 60.0"              --filter-name "FS60" \
    --filter-expression "MQ < 40.0"              --filter-name "MQ40" \
    --filter-expression "MQRankSum < -12.5"      --filter-name "MQRankSum-12.5" \
    --filter-expression "ReadPosRankSum < -8.0"  --filter-name "ReadPosRankSum-8" \
    -O results/HG002.snps.filtered.vcf.gz
```

Indels:

```bash
gatk VariantFiltration \
    -R data/ref/hg38_chr20_subset.fa \
    -V results/HG002.raw.vcf.gz \
    --select-type-to-include INDEL \
    --filter-expression "QD < 2.0"                --filter-name "QD2" \
    --filter-expression "FS > 200.0"              --filter-name "FS200" \
    --filter-expression "ReadPosRankSum < -20.0"  --filter-name "ReadPosRankSum-20" \
    -O results/HG002.indels.filtered.vcf.gz
```

### Step 4 — Merge and collect statistics

```bash
bcftools concat -a \
    results/HG002.snps.filtered.vcf.gz \
    results/HG002.indels.filtered.vcf.gz \
    -O z -o results/HG002.filtered.vcf.gz

bcftools index -t results/HG002.filtered.vcf.gz

bcftools stats results/HG002.filtered.vcf.gz > results/HG002.stats.txt
```

---

## Expected Outputs

```
results/
  HG002.g.vcf.gz                Per-sample GVCF with reference blocks
  HG002.raw.vcf.gz              Raw genotyped variants (pre-filter)
  HG002.snps.filtered.vcf.gz    SNPs with FILTER field populated
  HG002.indels.filtered.vcf.gz  Indels with FILTER field populated
  HG002.filtered.vcf.gz         Merged, indexed, filtered VCF
  HG002.stats.txt               bcftools stats summary
```

---

## How to Interpret Results

- **FILTER == PASS**: variant passes all hard filter thresholds; proceed to annotation
- **FILTER != PASS**: variant flagged by one or more expressions; treat as low-confidence
- **Ti/Tv ratio** (`bcftools stats`, field `Ts/Tv`): expected ~2.0–2.1 for whole-genome SNPs; values well outside this range indicate systematic calling errors
- **Indel size distribution**: most germline indels are 1–4 bp; a long tail of large indels suggests alignment or mapping artefacts
- **Number of variants**: for a single sample on a small demo interval, expect tens to low hundreds of variants depending on interval size and coverage

---

## Decision Guidelines

| Observation | Action |
|-------------|--------|
| Ti/Tv < 1.8 or > 2.2 | Revisit BAM quality (coverage, BQSR); check interval list for low-complexity regions |
| High fraction of FILTERED variants (> 30%) | Verify input BAM has adequate coverage; consider relaxing filter thresholds for low-coverage data |
| Zero PASS variants | Check reference genome version matches BAM header; verify interval file uses matching chromosome namespace (chr20 vs 20) |
| Large number of multi-allelic sites | Expected in some regions; split with `bcftools norm -m -any` before annotation |

---

## What This Affects Downstream

- **Module 04 (Variant Annotation)**: only PASS variants are typically annotated; FILTERED variants are carried through but deprioritized
- **Module 06 (GWAS) / Module 07 (PRS)**: variant call quality directly determines the reliability of any association signal; low-quality calls inflate false-positive rates
- **Benchmark evaluation**: HG002 GIAB calls can be compared against the PASS set using `hap.py` to compute precision and recall

---

## Key Concepts

**GVCF mode**: HaplotypeCaller emits a record for every site in the interval, including non-variant reference blocks. This enables joint genotyping across samples in cohort studies by combining per-sample GVCFs in a single GenotypeGVCFs step.

**Hard filtering vs VQSR**: Variant Quality Score Recalibration (VQSR) uses a Gaussian mixture model trained on known variant resources (dbSNP, HapMap) and is preferred for large cohorts (>30 samples). Hard filtering with fixed expression thresholds is used here because the demo dataset is a single sample; the filter expressions follow GATK best-practice recommendations.

**QD (QualByDepth)**: variant quality score normalized by depth. Low QD indicates a variant call that is only marginally supported relative to the coverage at that site.

**FS (FisherStrand)**: measures strand bias in read support for the variant allele. High FS values indicate that the variant is supported almost entirely on one strand, a common artefact.

---

## Results

The validated workflow on the HG002 demo interval produced:

- **14,051 variants** total (14,051 SNPs, 0 indels called in this interval)
- **Ts/Tv ratio = 2.11** — within the expected range for WGS SNP calls
- PASS-filtered VCF confirmed against GIAB benchmark for pipeline correctness

Screenshots:

- Read group addition confirming `SM:HG002` ![Read Group](figures/read_group_screenshot.png)
- bcftools stats output ![Bcftools Stats](figures/bcftools_stats_screenshot.png)

---

## What This Module Demonstrates

- GATK best-practice germline short variant discovery pipeline
- GVCF-mode calling structured for extensibility to multi-sample joint genotyping
- Application of GATK-recommended hard filter expressions for SNPs and indels separately
- Use of bcftools for VCF merging, indexing, and quality statistics
- Ti/Tv ratio and other standard QC metrics for evaluating call quality

---

## Real-World Usage

In production genomics pipelines:

- VQSR replaces hard filtering once cohort size exceeds ~30 WGS samples or ~100 exome samples
- `GenomicsDBImport` is used to consolidate per-sample GVCFs for joint genotyping at scale
- Variant calls are intersected with a capture interval BED (for exomes) or a PAR-masked BED (for WGS) before annotation
- dbSNP and gnomAD allele frequencies are added at this stage via GATK `VariantAnnotator` or Ensembl VEP in preparation for population-level filtering in module 04

---

## Next Step

Filtered variants are passed to **module 04 (variant annotation)** where each PASS variant is annotated with gene names, predicted functional consequences (VEP/SnpEff), and population allele frequencies from ClinVar and gnomAD.

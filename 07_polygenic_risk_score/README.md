# 07: Polygenic Risk Score (PRS)

## Objective

Aggregate per-variant GWAS effect sizes into a single per-sample polygenic risk score and evaluate score separation between cases and controls.

For each sample, the score is:

```
PRS = Σ  BETA_i × dosage_i
       i
```

where `dosage_i` is the allele count (0/1/2) at variant *i* and `BETA_i` is the log-odds weight derived from the module 06 GWAS.

---

## Why This Step Matters

Individual GWAS hits rarely have large effects. PRS aggregates small additive effects across many variants into a continuous score that captures an individual's inherited predisposition better than any single variant. Understanding how to derive weights, apply them to genotypes, and evaluate score distributions is foundational to modern complex-trait genomics.

This module demonstrates how GWAS summary statistics flow directly into a scoring workflow — the same conceptual path used in clinical risk stratification research, biobank-scale PRS studies, and multi-ancestry portability analyses.

---

## Summary

This module converts GWAS effect sizes into per-sample polygenic risk scores using PLINK and evaluates score distributions across case/control groups.

---

## End-to-End Workflow

This repository implements a complete genomics pipeline:

FASTQ → QC → Alignment → Variant Calling → Annotation → PCA → GWAS → PRS → eQTL → Nextflow

Each module is independently runnable and documented:

| Step | Module |
|------|--------|
| 01 | FASTQ QC |
| 02 | Alignment + BAM processing |
| 03 | Variant calling (GATK) |
| 04 | Variant annotation |
| 05 | Population PCA |
| 06 | GWAS |
| 07 | PRS |
| 08 | (optional / future) |
| 09 | GWAS → eQTL |
| 10 | Nextflow pipeline |

---

## Dataset

- **Genotypes**: QC-filtered PLINK binary fileset from module 05 (`demo_genotypes_qc.{bed,bim,fam}`) — 100 samples, ~1,000 SNPs
- **Phenotype**: Binary asthma labels from module 06 (PLINK coding: 1=control, 2=case)
- **Weights**: Derived directly from the module 06 `.assoc.logistic` output; BETA = ln(OR) per variant

Because the GWAS and scoring cohort are the same 100 samples, scores are in-sample and therefore optimistically biased due to overfitting. A production PRS derives weights from a large independent GWAS and applies them to a separate target dataset.

---

## Inputs

- GWAS summary statistics (`.assoc.logistic`)
- PLINK genotype files (`.bed/.bim/.fam`)
- Phenotype file

## Outputs

- Per-sample PRS (`.profile`)
- Merged phenotype + PRS table
- Summary statistics
- Visualization plots

---

## Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Python (pandas, numpy) | 3.x | Weight preparation, score merging, plotting |
| PLINK | 1.9 | Per-sample additive scoring (`--score`) |
| matplotlib | 3.x | Score distribution histogram and case/control boxplot |

**Platform note**: PLINK 1.9 is used for compatibility across architectures (including macOS arm64, where `plink2` Bioconda packages are not available). Output is `.profile` rather than `.sscore`; scoring logic is identical.

---

## Workflow Overview

```
.assoc.logistic (module 06)
    ↓
prepare_prs_weights.py            — filter to ADD test, drop invalid OR, compute BETA = ln(OR)
    ↓
plink --score                     — weight each sample's dosage by BETA, sum across variants
    ↓
merge_prs_pheno.py                — join .profile to phenotype; write per-group summary table
    ↓
plot_prs.py                       — histogram + case/control boxplot
```

---

## Workflow Orchestration (Nextflow)

Module 10 provides a Nextflow implementation of selected pipeline steps.

**Location:**  
`10_nextflow_pipeline/`

**What it includes:**
- DAG visualization  
- Reproducible execution  
- Modular pipeline definition  

**Run the workflow:**

```bash
cd 10_nextflow_pipeline
nextflow run main.nf
```
## Note:
This is a simplified demonstration workflow for portfolio purposes. Individual modules (01–09) remain the primary reference implementation.

## Environment Setup

Create and activate the main environment:

```bash
conda env create -f ../envs/genomics_pipeline.yml
conda activate genomics_pipeline
```

## Data Availability

This repository uses small simulated or subset datasets for demonstration.

Large files (BAM, full reference genomes, full VCFs) are intentionally excluded to keep the repository lightweight and portable.

To reproduce full workflows:
- Replace inputs with publicly available datasets (e.g., GIAB, 1000 Genomes)
- Or use the provided small demo datasets for testing pipeline logic

---

## Running the Analysis

```bash
conda activate genomics_pipeline
cd 07_polygenic_risk_score
```

### One command

```bash
bash scripts/run_prs.sh \
    ../05_population_pca/results/demo_genotypes_qc \
    ../06_asthma_gwas/results/asthma_pheno.txt \
    ../06_asthma_gwas/results/asthma_gwas.assoc.logistic \
    results/asthma_prs
```

The default P-value threshold is 0.5, which retains the majority of variants in this small simulated dataset. To apply a stricter threshold:

```bash
bash scripts/run_prs.sh \
    ../05_population_pca/results/demo_genotypes_qc \
    ../06_asthma_gwas/results/asthma_pheno.txt \
    ../06_asthma_gwas/results/asthma_gwas.assoc.logistic \
    results/asthma_prs_p05 \
    0.05
```

### Running steps individually

#### Step 0 — Prepare weights

```bash
python scripts/prepare_prs_weights.py \
    --gwas         ../06_asthma_gwas/results/asthma_gwas.assoc.logistic \
    --out          results/asthma_prs_weights.tsv \
    --p-threshold  0.05
```

Filters to ADD test rows, removes variants with missing or invalid OR, computes BETA = ln(OR), and writes a three-column PLINK score file (SNP A1 BETA).

#### Step 1 — Score

```bash
plink \
    --bfile ../05_population_pca/results/demo_genotypes_qc \
    --score results/asthma_prs_weights.tsv 1 2 3 header \
    --out   results/asthma_prs
```

Column positions: 1=SNP, 2=A1, 3=BETA. `header` instructs PLINK to skip the first line. Output: `results/asthma_prs.profile`.

#### Step 2 — Merge with phenotype

```bash
python scripts/merge_prs_pheno.py \
    --sscore results/asthma_prs.profile \
    --pheno  ../06_asthma_gwas/results/asthma_pheno.txt \
    --out    results/asthma_prs_merged.tsv
```

#### Step 3 — Plot

```bash
python scripts/plot_prs.py \
    --merged  results/asthma_prs_merged.tsv \
    --out-dir results/figures \
    --prefix  asthma_prs
```

---

## Expected Outputs

```
results/
  asthma_prs_weights.tsv           PLINK score file (SNP  A1  BETA)
  asthma_prs_weights_summary.tsv   GWAS columns + BETA for each selected variant
  asthma_prs.profile               PLINK 1.9 per-sample scores (FID IID PHENO CNT CNT2 SCORE)
  asthma_prs.log                   PLINK log — check "valid predictor" count
  asthma_prs_merged.tsv            PRS joined to phenotype (one row per sample)
  asthma_prs_summary.tsv           Per-group: n, mean, SD, median, min, max
  figures/
    asthma_prs_histogram.png       Score distribution coloured by case/control
    asthma_prs_boxplot.png         Median and spread per phenotype group
```

---

## How to Interpret Results

- **Score distribution (histogram)**: a roughly normal distribution is expected. Bimodal or strongly skewed distributions indicate a data issue (e.g., large numbers of missing variants, allele-coding mismatch).
- **Case/control separation (boxplot)**: with a simulated phenotype and in-sample weights, cases and controls will not cleanly separate. Any apparent separation reflects overfitting from using the same samples for GWAS and scoring, not true predictive signal.
- **`asthma_prs_summary.tsv`**: compare mean SCORE between cases (PHENO=2) and controls (PHENO=1). In a properly powered out-of-sample PRS, cases should have a higher mean score for a risk-increasing trait.
- **PLINK log**: the line `N valid predictors` (PLINK 1.9) or `valid scoring entries` (PLINK 2) shows how many weight-file variants were found in the genotype data. Unexpectedly low counts suggest a mismatch in SNP IDs or allele coding.
- **Why ln(OR) and not OR**: PLINK `--score` expects additive linear weights. Summing ln(OR) across variants is equivalent to computing the log of the product of individual ORs under a multiplicative model — the standard assumption in GWAS-based PRS.
- **Quantitative evaluation**: In real datasets, PRS performance is assessed using metrics such as AUC (for classification) or R² (for continuous traits). These are not meaningful in this simulated, in-sample setting but are critical for real-world interpretation.

---

## Common Pitfall

Using the same dataset for GWAS and PRS (in-sample scoring) leads to overfitting and inflated performance estimates. This module intentionally demonstrates this limitation.

---

## Decision Guidelines

| Observation | Action |
|-------------|--------|
| Zero valid predictors in PLINK log | Verify SNP IDs in weight file match the `.bim` file; check that A1 allele coding is consistent |
| Very few variants pass P threshold | Lower `--p-threshold` or confirm module 06 ran correctly and produced non-empty `.assoc.logistic` |
| Score distribution is degenerate (all identical or near-zero) | Inspect weight file for all-zero BETAs; check OR column in GWAS output for parsing errors |
| Boxplot shows no separation | Expected with in-sample simulated data; not a failure — it illustrates the overfitting problem |
| `asthma_prs_merged.tsv` has fewer rows than expected | Some IIDs in `.profile` may not match phenotype file IDs; check FID/IID formatting consistency |

---

## What This Affects Downstream

- **Module 09 (GWAS → eQTL)**: the SNPs selected as PRS variants overlap with the top GWAS hits sent to eQTL annotation; variants with large BETA values are the highest-priority candidates for functional follow-up  

- **Score transferability**: a real PRS derived here would need ancestry matching before application in a different cohort — a key consideration when interpreting results from module 05 PCA  

- **GWAS quality dependency**: PRS construction directly depends on GWAS quality. Inflated or poorly controlled GWAS results (e.g., high λ) will propagate into biased PRS weights.

Variants with large absolute BETA values contribute most strongly to the PRS and are primary candidates for functional interpretation.

---

## Key Concepts

**BETA = ln(OR)**: PLINK association output reports the odds ratio (OR), but scoring requires a linear additive weight. The log-odds (BETA) places the effect on a scale where: `BETA > 0` (OR > 1) means the A1 allele increases disease log-odds; `BETA < 0` (OR < 1) is protective; `BETA = 0` (OR = 1) is null.

**In-sample vs out-of-sample PRS**: using the same cohort for GWAS and scoring inflates apparent predictive performance because the weights are optimized to the training noise. Real PRS development uses external GWAS summary statistics (e.g., from GWAS Catalog or a biobank) applied to an independent target cohort.

**No LD adjustment**: this module uses a naive threshold-and-score approach. Production methods (LDpred2, PRS-CS) shrink BETAs toward zero based on LD structure, improving cross-ancestry portability and reducing overfitting. Ignoring LD leads to double-counting correlated variants, which inflates variance and reduces generalizability across datasets.

**Demo weight file**: `data/prs_weights_demo.tsv` contains 8 published asthma-associated rsIDs (ORMDL3, IL1RL1, IL13, FCER1A, IL18R1, RAD50) as a format reference. These will not match the simulated dataset's synthetic SNP IDs but demonstrate the weight file structure expected by real PRS tools.

---

## Results

The workflow completes on the 100-sample simulated dataset, producing a scored `.profile` file, a merged table with per-sample PRS and phenotype, and histogram/boxplot figures. The PLINK log confirms the number of variants scored. Score distributions are approximately normal. No meaningful case/control separation is expected given in-sample weights and a simulated phenotype — this outcome correctly illustrates both the PRS workflow and the overfitting problem. Observed score distributions reflect aggregation of many small effects rather than a few large-effect variants, consistent with the polygenic architecture of complex traits.

---

## What This Module Demonstrates

- Derivation of additive log-odds weights from GWAS logistic regression output
- Per-sample polygenic scoring using PLINK `--score`
- Score distribution visualization and case/control comparison
- Awareness of in-sample overfitting, LD confounding, and the limits of naive P-threshold selection
- Structured outputs feeding downstream eQTL and functional interpretation modules

---

## Real-World Usage

In production PRS studies:

- Weights are sourced from large independent GWAS (100k–1M+ samples) via the GWAS Catalog or PGS Catalog (e.g., PGS000043 for asthma)
- LD-aware shrinkage methods (LDpred2, PRS-CS, SBayesR) replace simple P-threshold selection to account for correlated variants
- Target cohorts are ancestry-matched to the discovery GWAS to minimize cross-ancestry score attenuation
- PRS performance is evaluated by AUC, Nagelkerke R², and OR per standard deviation of the score distribution
- Clinical translation requires calibration against population norms and integration with non-genetic risk factors

---

## Next Step

Top GWAS variants and their effect estimates feed into **module 09 (GWAS → eQTL)**, where the highest-ranked SNPs are cross-referenced against tissue-specific expression QTL data to generate mechanistic hypotheses about how risk variants influence gene expression in disease-relevant tissues.

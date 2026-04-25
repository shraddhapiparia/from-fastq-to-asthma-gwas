# 06: Asthma GWAS

## Objective

Run a genome-wide association study (GWAS) using logistic regression to identify genetic variants associated with a binary asthma phenotype. Produce Manhattan and QQ plots and a ranked list of top association signals for downstream eQTL interpretation.

---

## Why This Step Matters

GWAS is the primary method for identifying common genetic variants that influence disease risk at a population level. By testing the association between each SNP and the phenotype while controlling for population structure, GWAS produces a genome-wide ranked list of association signals. Without population stratification correction, systematic ancestry differences between cases and controls will produce false positives that inflate the genomic inflation factor (λ) and confound any biological interpretation. 

This module demonstrates the full GWAS workflow — phenotype preparation, association testing, and result visualization — using the QC-filtered genotypes and principal components from module 05. Principal components from module 05 are included as covariates to control for ancestry-driven confounding, ensuring that association signals reflect genotype–phenotype relationships rather than population structure.

---

## Dataset

- **Genotypes**: QC-filtered binary PLINK fileset from module 05 (`demo_genotypes_qc.{bed,bim,fam}`) — 100 samples, ~1,000 SNPs simulated via `plink --dummy`
- **Phenotype**: Binary asthma label (1=control, 2=case) simulated at 20% case prevalence with a weak correlation to PC1 to illustrate stratification effects
- **Covariates**: PC1–PC5 from the PCA computed in module 05, used to control for population stratification

The dataset is a reproducible subset designed to demonstrate the workflow at scale. SNP IDs are synthetic and used to illustrate association patterns and downstream interpretation.

---

## Tools

| Tool | Version | Purpose |
|------|---------|---------|
| PLINK | 1.9 | Logistic regression association testing |
| Python (pandas, numpy) | 3.x | Phenotype simulation and preparation |
| R (ggplot2, dplyr) | 4.x | Manhattan plot, QQ plot, top-hits table |

---

## Workflow Overview

```
QC genotypes + PCA eigenvectors (module 05)
    ↓
Phenotype preparation                 — simulate binary asthma labels, write PLINK pheno file
    ↓
Covariate file construction           — extract PC1–PC5 from eigenvec
    ↓
Logistic regression GWAS (PLINK)      — per-SNP association test, ADD model, PC covariates
    ↓
Manhattan + QQ plots (R)              — visualize association landscape, check inflation
    ↓
Top hits table                        → module 09 (GWAS → eQTL annotation)
```

---

## Running the Analysis

```bash
conda activate genomics_pipeline
cd 06_asthma_gwas
```

### One command

```bash
bash scripts/run_gwas.sh
```

Requires module 05 outputs to exist at `../05_population_pca/results/`.

### Running steps individually

#### Step 1 — Prepare phenotype

```bash
python scripts/01_prepare_pheno.py
```

Reads `../05_population_pca/results/demo_genotypes_pca.eigenvec`, simulates a binary phenotype with 20% case prevalence and a weak PC1 correlation, and writes `results/asthma_pheno.txt` in PLINK format (FID IID PHENO; 1=control, 2=case).

#### Step 2 — Run GWAS

```bash
bash scripts/02_run_gwas.sh
```

Extracts PC1–PC5 from the eigenvec file into `results/pca_covariates.txt`, then runs:

```bash
plink \
    --bfile ../05_population_pca/results/demo_genotypes_qc \
    --pheno results/asthma_pheno.txt \
    --covar results/pca_covariates.txt \
    --logistic hide-covar \
    --allow-no-sex \
    --out results/asthma_gwas
```

`--hide-covar` suppresses per-covariate rows from the output; only the ADD (additive) test rows are retained.

#### Step 3 — Plot results

```bash
Rscript scripts/03_plot_manhattan_qq.R
```

Filters the `.assoc.logistic` file to ADD test rows with valid P-values, computes the genomic inflation factor λ from the median chi-squared statistic, and writes Manhattan and QQ plots plus a top-10 hits table.

---

## Expected Outputs

```
results/
  asthma_pheno.txt                  PLINK phenotype file (FID IID PHENO)
  pca_covariates.txt                PC1–PC5 covariate file
  asthma_gwas.assoc.logistic        Full GWAS results (CHR SNP BP A1 TEST NMISS OR STAT P)
  top_hits.tsv                      Top 10 SNPs sorted by P-value

figures/
  manhattan_plot.png                −log10(P) by genomic position, genome-wide significance line at 5×10⁻⁸
  qq_plot.png                       Observed vs expected −log10(P) with λ in title
```

---

## How to Interpret Results

- **Manhattan plot**: each point is a SNP; the y-axis is −log₁₀(P). Variants crossing the dashed red line (P = 5×10⁻⁸) meet the conventional genome-wide significance threshold. With 1,000 SNPs and 100 samples this threshold will rarely be reached; the plot demonstrates the visualization pattern, not a powered discovery.
- **QQ plot**: plots observed −log₁₀(P) quantiles against expected quantiles under the null. Deviation above the diagonal indicates inflated test statistics. λ is computed as the median observed chi-squared divided by the median expected chi-squared under the null (0.456); λ ≈ 1 indicates well-controlled stratification.
Systematic early deviation in the QQ plot (before the tail) indicates population stratification or confounding, while deviation only in the tail suggests true association signals.
- **Genomic inflation factor (λ)**: values modestly above 1.0 are expected here because the simulated phenotype encodes a deliberate weak correlation with PC1, illustrating what uncorrected stratification looks like. Including PC1–PC5 as covariates partially attenuates this.
- **OR (odds ratio)**: values > 1 indicate the A1 allele is more frequent in cases; values < 1 indicate it is more frequent in controls. For a simulated phenotype these directions are arbitrary.

---

## Decision Guidelines

| Observation | Action |
|-------------|--------|
| λ > 1.10 | Verify PC covariates are included; consider adding more PCs or checking for cryptic relatedness |
| λ < 0.95 | Possible over-correction or data issue; check phenotype coding (must be 1/2, not 0/1) |
| No rows in output after TEST == "ADD" filter | Confirm PLINK ran without error; check that `--hide-covar` did not remove all rows in older PLINK builds |
| All P-values near 1 | Inspect phenotype file for all-control or all-case samples; check `--pheno` path is correct |
| Zero variants in top_hits.tsv | Script writes the top 10 regardless of threshold — check that the `.assoc.logistic` file is non-empty |

---

## What This Affects Downstream

- **Module 07 (Polygenic Risk Score)**: GWAS effect sizes (log(OR)) and P-values are used to construct PRS weights; variant selection thresholds directly influence score performance
- **Module 09 (GWAS → eQTL)**: the top-ranked SNP IDs from `top_hits.tsv` are cross-referenced against the eQTL reference to identify variants with potential regulatory consequences
- **Stratification**: the inclusion of PC covariates here directly controls the inflation that would otherwise propagate into any downstream prioritization

---

## Key Concepts

**Logistic regression (ADD model)**: tests the additive effect of each SNP (0, 1, or 2 copies of the effect allele) on log-odds of case status. The ADD model is the standard first-pass test in binary-trait GWAS.

**Genomic inflation factor (λ)**: summarizes systematic deviation of the observed test statistic distribution from the null. Computed as median(χ²_observed) / 0.456, where 0.456 is the median of a χ²(1) distribution. Inflation above 1.0 typically indicates uncorrected population stratification or cryptic relatedness.

**PLINK phenotype coding**: PLINK logistic regression expects 1=control, 2=case. A value of 0 is treated as missing. The Python script adds 1 to a 0/1 binary vector to produce the required encoding.

**Genome-wide significance threshold (5×10⁻⁸)**: derived from Bonferroni correction for ~1 million independent tests across the human genome. With only 1,000 SNPs the effective threshold would be 5×10⁻⁵, but the canonical line is shown to demonstrate conventional reporting.

---

## Results

The workflow completes on the 100-sample simulated dataset and produces a non-empty `.assoc.logistic` file, Manhattan and QQ plots, and a top-hits table. The QQ plot shows modest inflation (λ slightly above 1.0) consistent with the intentional PC1–phenotype correlation baked into the simulation. No variants reach genome-wide significance at 5×10⁻⁸ in a 100-sample, 1,000-SNP dataset, which is expected given the sample size.
Top-ranked variants reflect the simulated genotype–phenotype correlation and serve as inputs for downstream PRS construction and eQTL annotation.

---

## What This Module Demonstrates

- Binary-trait GWAS using logistic regression with population structure covariates
- PLINK phenotype file preparation and covariate construction from PCA output
- Manhattan and QQ plot generation in R with ggplot2
- Genomic inflation factor (λ) computation using the correct chi-squared formula
- Structured output suitable for downstream PRS and eQTL modules

---

## Real-World Usage

In production GWAS studies:

- Sample sizes range from thousands (rare disease) to hundreds of thousands (biobank-scale)
- Phenotype harmonization across cohorts requires careful curation of ICD codes, self-reported data, and clinical records
- Mixed-model association tests (BOLT-LMM, SAIGE, REGENIE) replace logistic regression at biobank scale to handle relatedness and unbalanced case/control ratios
- Post-GWAS steps include LD clumping, fine-mapping, and colocalization rather than direct SNP-level interpretation
- Summary statistics are deposited in public resources (GWAS Catalog, OpenGWAS) for meta-analysis and downstream integration

---

## Next Step

Top GWAS hits are passed to **module 07 (Polygenoc Risk Score)** where association summary statistics are used to construct a polygenic risk score, and to **module 09 (GWAS → eQTL)** where top SNPs are cross-referenced against tissue-specific expression QTL data to generate mechanistic hypotheses.

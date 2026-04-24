# 04: Variant Annotation

## Objective

Add biological context to PASS-filtered variants from module 03 by extracting per-variant quality metrics and functional fields. Produce an annotated summary ready for variant prioritization and downstream interpretation.

---

## Why This Step Matters

A raw VCF contains genomic coordinates and quality scores, but no biological meaning. Annotation maps each variant onto gene models and functional context: which gene is affected, what consequence the variant has on the transcript, how common it is in reference populations, and whether it has been previously associated with disease. Without annotation, there is no principled basis for deciding which variants to prioritize for follow-up.

For GWAS and population studies (modules 06–09), annotation informs variant filtering and interpretation after association testing. For clinical applications, annotation is the step that distinguishes a rare missense variant in a disease gene from a common synonymous change in an intron.

---

## Dataset

- **Input VCF**: PASS-filtered variants from module 03 (`../03_variant_calling_gatk/results/HG002_chr20_10_20Mb.filtered.vcf.gz`)
- **Sample**: HG002 (Genome in a Bottle) — chr20:10,000,000–20,000,000 interval
- **Variant count**: 14,051 SNPs, 0 indels in this interval

---

## Tools

| Tool | Version | Purpose |
|------|---------|---------|
| bcftools | 1.x | VCF querying, variant counting, field extraction |
| Ensembl VEP | 110+ | Full functional annotation (gene, consequence, population frequency) — see Real-World Usage |

---

## Workflow Overview

```
Filtered VCF (module 03)
    ↓
Variant counting                  — total, SNPs, indels
    ↓
Field extraction (bcftools query) — CHROM, POS, REF, ALT, QUAL, DP per variant
    ↓
Annotation summary                → variant prioritization, downstream modules
```

Full functional annotation (consequence prediction, allele frequency lookup, pathogenicity scoring) requires VEP or ANNOVAR; see Real-World Usage for the production workflow.

---

## Running the Analysis

```bash
conda activate variant-annotation
cd 04_variant_annotation
```

### Step 1 — Run annotation script

```bash
bash scripts/annotate_variants.sh \
    ../03_variant_calling_gatk/results/HG002_chr20_10_20Mb.filtered.vcf.gz \
    results/HG002_chr20_10_20Mb.annotation_summary.txt
```

The script counts total variants by type and extracts per-variant fields using `bcftools query`.

### Step 2 — Inspect results

```bash
cat results/HG002_chr20_10_20Mb.annotation_summary.txt
```

---

## Expected Outputs

```
results/
  HG002_chr20_10_20Mb.annotation_summary.txt    Variant counts + per-variant CHROM/POS/REF/ALT/QUAL/DP table
```

### Example output format

```
Variant Summary
===============
Input VCF: results/HG002_chr20_10_20Mb.filtered.vcf.gz
Total variants: 14051
SNPs: 14051
Indels: 0

Example variants:
CHROM    POS        REF  ALT  QUAL  INFO_DP
chr20    10000001   G    A    45    30
chr20    10000002   C    T    50    28
chr20    10000003   T    C    48    32
```

---

## How to Interpret Results

### Variant counts

- **SNP:indel ratio**: a high ratio (many SNPs, few indels) is expected for short-read WGS. A disproportionate number of indels relative to the Ti/Tv check from module 03 may indicate alignment or calling artefacts.
- **Total count vs PASS count**: the summary operates on the already-filtered VCF from module 03; all variants here are PASS-filtered.

### Per-variant fields

- **QUAL**: phred-scaled variant quality. Values below 30 warrant caution even after PASS filtering in some pipelines.
- **DP (INFO/DP)**: total read depth at the site. Very low DP (<10×) increases genotype uncertainty; very high DP may indicate a collapsed repeat region.
- **REF/ALT**: confirm that variant calls are biallelic for standard annotation tools. Multi-allelic sites should be split with `bcftools norm -m -any` before VEP annotation.

### Biological interpretation (with VEP)

When full annotation is applied, the interpretation logic is:

| Consequence | Interpretation |
|-------------|---------------|
| Stop gained / frameshift | High impact — likely loss of function; prioritize for functional follow-up |
| Missense | Moderate impact — assess PolyPhen2/SIFT scores and population frequency |
| Synonymous | Low impact — usually filtered out unless in regulatory context |
| Intronic / intergenic | Lowest coding impact — may have regulatory function; check eQTL databases |

Population frequency from gnomAD provides the other axis of prioritization:

- **AF < 0.01 (rare)**: variants absent from or rare in reference populations are more likely to be functionally relevant, especially if high-impact
- **AF > 0.05 (common)**: common variants are unlikely to be highly deleterious but are the primary focus of GWAS
- **ClinVar pathogenic/likely pathogenic**: clinical precedent for disease association; treat as high priority regardless of consequence class

---

## Decision Guidelines

| Observation | Action |
|-------------|--------|
| High-impact variant (stop gain, frameshift) in a disease-relevant gene | Prioritize for functional validation; check ClinVar and literature |
| Rare missense (AF < 0.01) with damaging prediction | Flag for burden testing (module 08) and manual review |
| Common synonymous variant | Deprioritize for rare variant analysis; include in GWAS cohort |
| Very low QUAL or DP | Revisit variant calling filters; consider excluding from downstream analysis |
| Multi-allelic site | Split with `bcftools norm -m -any` before passing to annotation tools |
| Variant absent from dbSNP | May be novel; confirm with increased depth or orthogonal method before reporting |

---

## What This Affects Downstream

- **Module 06 (GWAS)**: annotation confirms that GWAS-significant variants are real calls with sufficient quality; functional consequence informs biological interpretation of hits
- **Module 08 (Rare variant testing)**: rare high-impact variants identified here are the primary inputs for gene-level burden testing
- **Module 09 (GWAS → eQTL)**: noncoding GWAS hits annotated as regulatory candidates are prioritized for eQTL overlap
- **Clinical reporting**: ClinVar pathogenicity and gnomAD frequency determine whether a variant is reportable in a clinical setting

---

## Key Concepts

**Variant consequence hierarchy**: stop gained > frameshift > splice site > missense > synonymous > intronic > intergenic, ordered by expected functional impact. High-consequence variants are rare; most variants called in a WGS sample are intronic or intergenic.

**Population frequency vs functional impact**: these are independent axes. A common missense variant may be benign (selected against deleterious alleles over generations). A rare intronic variant may be a strong eQTL. Both dimensions must be considered together when prioritizing.

**bcftools query vs VEP**: `bcftools query` extracts fields already present in the VCF (QUAL, DP, alleles). Ensembl VEP runs the variant against gene model, population frequency, and pathogenicity databases to generate consequence annotations not present in the raw VCF. This module demonstrates the extraction layer; VEP adds the biological interpretation layer.

---

## Results

The annotation script confirmed 14,051 PASS-filtered SNPs and 0 indels in the HG002 chr20:10–20 Mb interval. Per-variant quality and depth fields were extracted successfully. Typical QUAL values range from 30–100 and DP from 20–60× for this Genome in a Bottle benchmark sample, consistent with high-confidence callable regions.

![Annotation Summary](figures/annotation_summary_screenshot.png)

---

## What This Module Demonstrates

- bcftools-based VCF field extraction and variant classification
- Structured variant prioritization logic (consequence × frequency)
- Awareness of full annotation toolchains (VEP, ClinVar, gnomAD) and their role in production workflows
- Connection between raw variant quality metrics and downstream biological interpretation

---

## Real-World Usage

In production annotation pipelines:

- **Ensembl VEP** is run with `--everything` or a curated plugin set: CADD, PolyPhen-2, SIFT, REVEL, SpliceAI, gnomAD allele frequencies, ClinVar
- Variants are filtered to a final working set: PASS + high/moderate consequence, or all variants with MAF-stratified tiers
- **ANNOVAR** is commonly used in clinical pipelines for its structured output format and OMIM integration
- Large cohort projects annotate once at the VCF level and store results in a database (Hail, Variant Warehouse) to avoid re-annotating per analysis
- Variant consequence and population frequency together determine whether a variant enters rare variant burden testing (module 08) or GWAS filtering (module 06)

---

## Next Step

Annotated variants feed into **module 05 (population PCA)** for genotype QC and ancestry inference, and into **module 06 (GWAS)** where association testing connects variant positions to phenotype. High-impact rare variants identified here are carried forward to **module 08 (rare variant testing)** for gene-level burden analysis.

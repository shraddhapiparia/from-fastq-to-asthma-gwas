# 04_variant_annotation

Objective
---------

This module demonstrates basic variant annotation using lightweight tools suitable for a portfolio project. It shows how to add biological context to variants from a VCF file, focusing on interpretation rather than comprehensive clinical annotation. For demonstration, it uses bcftools to query and interpret variants, with optional VEP documentation.

Dataset
-------

- Example VCF: the filtered VCF from `03_variant_calling_gatk/results/sample_filtered.vcf.gz`.

Tools
-----

- `bcftools` — for querying and annotating VCFs
- `ensembl-vep` (optional) — for comprehensive annotation if installed
- `bash` — wrapper scripts

Folder structure
----------------

- `scripts/` — helper scripts (`annotate_variants.sh`)
- `results/` — example outputs (tracked with `.gitkeep`)
- `figures/` — placeholder figures for a report (tracked with `.gitkeep`)
- `environment.yml` — conda environment spec for this module

Workflow overview
-----------------

1. Query the VCF for basic variant information.
2. Add lightweight annotations (e.g., variant type, allele frequency if available).
3. Generate a summary report or annotated VCF.

Required inputs
---------------

- **Filtered VCF**: from Project 03 (e.g., `results/sample_filtered.vcf.gz`)
- **Reference FASTA** (optional for some annotations): `refs/toy_reference.fa`

Commands to run locally
-----------------------

**Prerequisites:** Activate the conda environment.

```bash
conda activate variant-annotation
cd 04_variant_annotation
```

**Step 1: Run annotation script**

```bash
bash scripts/annotate_variants.sh \
  ../03_variant_calling_gatk/results/HG002_chr20_10_20Mb.filtered.vcf.gz \
  results/HG002_chr20_10_20Mb.annotation_summary.txt
```

**Step 2: Inspect results**

```bash
cat results/HG002_chr20_10_20Mb.annotation_summary.txt
```

Expected outputs
----------------

- `results/annotated_summary.txt` — a text summary of variants with basic annotations

What annotation means in genomics
----------------------------------

Annotation adds biological context to variants, such as gene names, functional consequences, population frequencies, and pathogenicity scores. This helps interpret whether a variant is likely benign, pathogenic, or of unknown significance.

Example fields to interpret
---------------------------

- **Gene**: which gene the variant affects
- **Consequence**: e.g., missense, synonymous, frameshift
- **Allele frequency**: how common the variant is in populations
- **Pathogenicity**: scores like CADD, PolyPhen

What this implies
-----------------

This module provides a starting point for variant interpretation. For real projects, use comprehensive tools like VEP or ANNOVAR. Here, we focus on lightweight querying to demonstrate the concept without heavy setup.

Results
-------

The annotation summary for the HG002 chr20 interval variants:

- **14,051 variants** total
- **14,051 SNPs**
- **0 indels**

Example variant positions and depth values:

```
CHROM	POS	REF	ALT	QUAL	INFO_DP
chr20	10000001	G	A	45	30
chr20	10000002	C	T	50	28
chr20	10000003	T	C	48	32
...
```

![Annotation Summary](figures/annotation_summary_screenshot.png)

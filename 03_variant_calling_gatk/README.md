# 03_variant_calling_gatk

Objective
---------

This module demonstrates variant calling using GATK HaplotypeCaller on a tiny mapped demo BAM file. It shows how to call SNPs and indels from aligned reads, then apply basic filtering with bcftools. The goal is to produce a small VCF file for downstream analysis, illustrating the core steps in a lightweight, educational manner.

Dataset
-------

- Example BAM: HG002 (Ashkenazim Trio son) chr20 10-20Mb interval, subset from full 300x BAM.
- Truth VCF: HG002 benchmark VCF for comparison.
- Reference FASTA: GRCh38 human reference genome.

Tools
-----

- `gatk` — GATK4 HaplotypeCaller for variant calling
- `bcftools` — for basic variant filtering and manipulation
- `samtools` — for BAM indexing and subsetting
- `bash` — wrapper scripts

Folder structure
----------------

- `scripts/` — helper scripts (`run_haplotypecaller.sh`, `filter_variants.sh`)
- `data/` — demo data directory (download BAM, VCF, and reference here)
- `results/` — example outputs (tracked with `.gitkeep`)
- `figures/` — placeholder figures for a report (tracked with `.gitkeep`)
- `environment.yml` — conda environment spec for this module

Workflow overview
-----------------

1. Download HG002 BAM, truth VCF, and GRCh38 reference.
2. Subset BAM and VCF to chr20:10000000-20000000 interval.
3. Add read groups to BAM.
4. Index reference and BAM.
5. Run GATK HaplotypeCaller to produce VCF.
6. Filter variants with bcftools.

Required inputs
---------------

- **Reference FASTA**: GRCh38 (e.g., `data/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna.gz`)
- **FASTA index**: created with `samtools faidx`
- **Sequence dictionary**: created with `gatk CreateSequenceDictionary`
- **BAM file**: subset HG002 BAM (e.g., `data/HG002_chr20_10_20Mb.bam`)
- **BAM index**: created with `samtools index`

Download Demo Data
------------------

Download HG002 data for chr20 interval demonstration:

```bash
mkdir -p data
cd data

# Download reference FASTA
curl -L -o GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna.gz \
  https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/001/405/GCF_000001405.40_GRCh38.p14/GRCh38_major_release_seqs_for_alignment_pipelines/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna.gz

# Download HG002 BAM (full, then subset locally)
curl -L -o HG002.GRCh38.300x.bam \
  https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/data/AshkenazimTrio/HG002_NA24385_son/NIST_HiSeq_HG002_Homogeneity-10953946/NHGRI_Illumina300X_AJtrio_novoalign_bams/HG002.GRCh38.300x.bam

# Download truth VCF
curl -L -o HG002_GRCh38_1_22_v4.2.1_benchmark.vcf.gz \
  https://storage.googleapis.com/deepvariant/case-study-testdata/HG002_GRCh38_1_22_v4.2.1_benchmark.vcf.gz

cd ..
```

Commands to run locally
-----------------------

**Prerequisites:** Activate the conda environment and download demo data.

```bash
conda activate variant-calling-gatk
cd 03_variant_calling_gatk
```

**Step 1: Subset BAM and VCF to chr20:10000000-20000000**

```bash
# Subset BAM
samtools view -b data/HG002.GRCh38.300x.bam chr20:10000000-20000000 > data/HG002_chr20_10_20Mb.bam

# Index subset BAM
samtools index data/HG002_chr20_10_20Mb.bam

# Subset truth VCF
bcftools view -r chr20:10000000-20000000 data/HG002_GRCh38_1_22_v4.2.1_benchmark.vcf.gz -Oz -o data/HG002_chr20_10_20Mb_truth.vcf.gz
bcftools index data/HG002_chr20_10_20Mb_truth.vcf.gz
```

**Step 2: Prepare reference**

```bash
# Index reference
samtools faidx data/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna.gz

# Create sequence dictionary
gatk CreateSequenceDictionary \
  -R data/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna.gz \
  -O data/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna.dict
```

**Step 3: Add read groups to BAM**

```bash
gatk AddOrReplaceReadGroups \
  -I data/HG002_chr20_10_20Mb.bam \
  -O data/HG002_chr20_10_20Mb.RG.bam \
  --RGID HG002 \
  --RGLB lib1 \
  --RGPL ILLUMINA \
  --RGPU unit1 \
  --RGSM HG002

# Index RG-added BAM
samtools index data/HG002_chr20_10_20Mb.RG.bam
```

**Step 4: Run HaplotypeCaller**

```bash
bash scripts/run_haplotypecaller.sh \
  data/GCA_000001405.15_GRCh38_no_alt_plus_hs38d1_analysis_set.fna.gz \
  data/HG002_chr20_10_20Mb.RG.bam \
  results/HG002_chr20_10_20Mb.vcf.gz
```

**Step 5: Filter variants**

```bash
bash scripts/filter_variants.sh \
  results/HG002_chr20_10_20Mb.vcf.gz \
  results/HG002_chr20_10_20Mb.filtered.vcf.gz
```

**Step 6: Inspect results**

```bash
# View header and first few variants
bcftools view -h results/HG002_chr20_10_20Mb.filtered.vcf.gz | head -20
bcftools view results/HG002_chr20_10_20Mb.filtered.vcf.gz | head -10

# Generate stats
bcftools stats results/HG002_chr20_10_20Mb.filtered.vcf.gz > results/HG002_chr20_10_20Mb.stats.txt
```

Expected outputs
----------------

- `results/sample.vcf.gz` — raw VCF from HaplotypeCaller
- `results/sample_filtered.vcf.gz` — filtered VCF after bcftools processing
- Associated index files (`.tbi`) for tabix indexing

What a VCF file is
------------------

VCF (Variant Call Format) is a text file format for storing genetic variation data. Each line represents a variant position, with columns describing the chromosome, position, reference allele, alternate alleles, quality scores, and genotype information for samples.

Meaning of common VCF fields
----------------------------

- **CHROM**: chromosome or contig name
- **POS**: position on the chromosome (1-based)
- **REF**: reference allele sequence
- **ALT**: alternate allele(s) observed
- **QUAL**: quality score (phred-scaled probability of error)
- **FILTER**: pass/fail status based on filters
- **GT**: genotype (e.g., 0/0 = homozygous reference, 0/1 = heterozygous)
- **DP**: read depth at the position

What this implies
-----------------

This module illustrates the transition from aligned reads (BAM) to called variants (VCF), a key step in genomics pipelines. The example uses a real HG002 interval to produce authentic variants. For real datasets, variant calling requires careful parameter tuning, quality control, and often joint calling across samples. Use this as a starting point for understanding variant detection workflows.

Results
-------

The validated workflow produced the following results for the HG002 chr20:10000000-20000000 interval:

- **1 sample** (HG002)
- **14,051 variants** total
- **14,051 SNPs**
- **0 indels**
- **Ts/Tv ratio = 2.11**

Screenshots of the workflow:

- Read group addition showing `SM:HG002` ![Read Group](figures/read_group_screenshot.png)
- Bcftools stats output ![Bcftools Stats](figures/bcftools_stats_screenshot.png)

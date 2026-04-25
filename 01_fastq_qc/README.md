# 01: FASTQ Quality Control

## Objective

Assess sequencing quality using FastQC and MultiQC, and determine whether data are suitable for downstream analysis such as alignment and variant calling.

---

## Why This Step Matters

Sequencing errors and library preparation artifacts can introduce biases that propagate through the entire pipeline.

Common issues include:
- Low-quality base calls
- Adapter contamination
- GC bias
- Overrepresented sequences

Identifying these early helps decide whether to:
- Proceed with analysis
- Trim reads
- Filter samples
- Re-run sequencing

---

## Dataset

This module uses a small demonstration FASTQ derived from public test data (NA12878 / Genome in a Bottle).

The dataset is intentionally small to allow fast execution while preserving typical QC patterns.

---

## Tools

- FastQC — per-sample quality metrics  
- MultiQC — aggregate report across samples  
- seqtk (optional) — subsampling  

---

## Workflow

1. Obtain or generate a small FASTQ file  
2. Run FastQC on the FASTQ  
3. Aggregate results using MultiQC  

---

## Running the Analysis

### Setup environment
```bash
conda env create -f ../envs/genomics_pipeline.yml
conda activate genomics_pipeline
```

### Download example data

```bash
curl -L -o data/NA12878_small_R1.fastq.gz https://raw.githubusercontent.com/jdidion/atropos/master/tests/data/small.fastq.gz
```

### Run FastQC

```bash
bash scripts/run_fastqc.sh data/NA12878_small_R1.fastq.gz results/fastqc -t 4
```

### Run MultiQC

```bash
bash scripts/run_multiqc.sh results/fastqc results/multiqc
```

---

## Expected Outputs

- FastQC reports (*_fastqc.html*)  
- MultiQC report (multiqc_report.html)  

---

## How to Interpret Results

### Key metrics

Per-base sequence quality  
- High median quality across read positions → good data  
- Drop at 3′ end → common, may require trimming  

Adapter content  
- High adapter signal → trim reads before alignment  

GC content  
- Large deviation from expected distribution → possible contamination or bias  

---

## Decision Guidelines

Use QC results to guide next steps:

- Good quality, no adapter contamination → proceed to alignment  
- Adapter contamination detected → perform trimming (e.g., cutadapt)  
- Low-quality tails → trim low-quality bases  
- Severe issues → consider excluding sample  

---

## What This Affects Downstream

QC directly impacts:

- Alignment rate  
- Variant calling accuracy  
- False positive variants  

Poor QC → poor alignment → unreliable variants  

---

## Limitations

- Small FASTQ file does not fully represent real sequencing runs  
- Some warnings are expected due to small sample size  
- Metrics should be interpreted as demonstration, not real QC thresholds  

---

## Real-World Usage

In real sequencing projects:

- QC is run on all samples before alignment  
- Trimming and filtering are applied based on QC  
- Failed samples are removed early to avoid downstream bias  

---

## Next Step

Proceed to:

02_alignment_bam_processing

to align reads and generate BAM files for variant calling.
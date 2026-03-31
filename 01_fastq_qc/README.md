# 01_fastq_qc

Objective
---------

Provide a lightweight, reproducible sequencing quality-control (QC) example using a small NA12878 / Genome in a Bottle FASTQ subset. This module demonstrates how to run FastQC and aggregate results with MultiQC, explains key QC metrics, and includes two minimal helper scripts to run the steps reproducibly.

Dataset
-------

- Example dataset: a small demonstration FASTQ derived from public test data. The repository does not include large raw FASTQ files; instead this module shows how to fetch a tiny example FASTQ for demonstration purposes.

Tools
-----

- FastQC — per-file sequencing QC (https://www.bioinformatics.babraham.ac.uk/projects/fastqc/)
- MultiQC — aggregate QC reports into one HTML summary (https://multiqc.info/)
- seqtk — optional, for FASTQ subsampling (https://github.com/lh3/seqtk)
- wget / curl — for fetching example files if desired

Workflow
--------

1. Obtain or create a small FASTQ sample (subsample a larger NA12878 FASTQ if needed).
2. Run FastQC on the FASTQ sample(s).
3. Run MultiQC on the FastQC output to generate a consolidated report.

Commands
--------


Download Example Data
---------------------

Fetch a small demonstration FASTQ (used in this README). This file is a public test FASTQ that is suitable for a quick FastQC/MultiQC demo:

```bash
curl -L -o data/NA12878_small_R1.fastq.gz https://raw.githubusercontent.com/jdidion/atropos/master/tests/data/small.fastq.gz
```

1) (Optional) Create a small example FASTQ by subsampling a large FASTQ (example):

```bash
# If you have a large gzipped FASTQ (large_R1.fastq.gz), subsample reads with seqtk:
zcat large_R1.fastq.gz | seqtk sample -s100 - 10000 | gzip > NA12878_small_R1.fastq.gz

# Replace `10000` with the number of reads you want in the small example.
```

2) Run FastQC using the helper script (script accepts FASTQ files followed by an output directory; optional `-t` threads flag):

```bash
# Example: run FastQC with 4 threads (as run in this project)
bash scripts/run_fastqc.sh data/NA12878_small_R1.fastq.gz results/fastqc -t 4
```

3) Run MultiQC using the helper script (point it to the FastQC results directory and an output directory for the MultiQC report):

```bash
bash scripts/run_multiqc.sh results/fastqc results/multiqc
```

Expected outputs
----------------

- FastQC per-sample files in the FastQC output directory: `*_fastqc.html` and `*_fastqc.zip` for each FASTQ.
- A `multiqc_report.html` and associated data files in the MultiQC output directory.

Interpretation
--------------

Why sequencing QC is necessary

Sequencing and library preparation can produce systematic issues (low-quality cycles, adapter carryover, biased GC, contamination). QC enables early detection of these problems so you can decide whether to trim reads, remove samples, or repeat library prep before investing time in alignment and variant calling.

Example FastQC output descriptions

- Per-base sequence quality: a per-cycle boxplot of quality scores (y-axis = quality score, x-axis = position in read). Good data usually shows high median quality and tight interquartile ranges across most positions. Systematic drops toward the 3' end are common and may require trimming.

- Adapter contamination: reports occurrences of known adapter sequences in reads. If frequent adapters are detected, trimming adapters before alignment is recommended. The FastQC report highlights which adapter sequences matched and where in reads they occur.

- GC content: shows the distribution of GC percentage across all reads versus the theoretical distribution for a random library. Large deviations or unexpected peaks can indicate contamination or strong library bias.

Lightweight and realistic choices
--------------------------------

- This project is intentionally small: you create or download a small NA12878 FASTQ subset rather than storing large raw FASTQ files in the repository.
- Scripts are minimal wrappers that check for required programs and forward arguments to `fastqc` and `multiqc`.

Next steps
----------

- If QC looks good, proceed to [../02_alignment_bam_processing/README.md](../02_alignment_bam_processing/README.md) to align, sort, and mark duplicates on the reads.

Commands Run
------------

The commands actually executed for this demonstration (performed after activating the `genomics-qc` environment):

```bash
conda activate genomics-qc
bash scripts/run_fastqc.sh data/NA12878_small_R1.fastq.gz results/fastqc -t 4
bash scripts/run_multiqc.sh results/fastqc results/multiqc
```

Example Results
---------------

- FastQC summary: overall PASS reported in the MultiQC summary for the provided tiny FASTQ (see `figures/fastqc_summary.png`).
- Per-base sequence quality: PASS — quality scores across positions are high for this short demonstration file (see `figures/per_base_quality.png`).
- Adapter content: PASS — no major adapter contamination detected for the example file (see `figures/overrepresented_sequences.png`).
- Notes: this is a very small demonstration FASTQ and MultiQC/FastQC may report warnings or failures that are expected for tiny or contrived test files (e.g., low sequence count, unusual duplication metrics). Treat these as demonstration artifacts rather than sequencing-run quality problems.

Interpretation summary
----------------------

The QC report for this tiny example indicates generally good per-base quality and no obvious adapter contamination; however, some warnings are expected because the sample is intentionally small and not representative of a real sequencing run. For real datasets, use these QC results to decide whether trimming, additional filtering, or re-sequencing is needed before alignment and variant calling.

Conda environment (recommended)
-----------------------------

We provide a small conda environment spec for this module that installs `fastqc`, `multiqc`, and `seqtk`.

Create the environment and activate it:

```bash
# Using conda
conda env create -f 01_fastq_qc/environment.yml
conda activate genomics-qc

# Or, if you have mamba installed (faster):
mamba env create -f 01_fastq_qc/environment.yml
mamba activate genomics-qc
```

After activating the environment, `fastqc` and `multiqc` will be available on your PATH and you can run the helper scripts in `01_fastq_qc/scripts/`.

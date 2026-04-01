# 02_alignment_bam_processing

Objective
---------

This lightweight module demonstrates read alignment and basic BAM processing for a small example FASTQ (from Project 01). It shows how to align reads with `bwa`, convert SAM to BAM with `samtools`, sort and index BAMs, mark duplicates with `picard`, and collect basic alignment statistics with `samtools flagstat`.

Dataset
-------

- Example FASTQ (used here): `data/NA12878_small_R1.fastq.gz` (same file from `01_fastq_qc`). This is a small demonstration FASTQ suitable for testing the commands; it is not representative of a full sequencing run.

Tools
-----

- `bwa` — alignment (mem)
- `samtools` — SAM/BAM conversion, sorting, indexing, and `flagstat`
- `picard` — MarkDuplicates
- `bash` — wrapper scripts

Folder structure
----------------

- `scripts/` — helper scripts (`run_alignment.sh`, `process_bam.sh`)
- `results/` — example outputs (tracked with `.gitkeep`)
- `figures/` — placeholder figures for a report (tracked with `.gitkeep`)
- `environment.yml` — conda environment spec for this module

Workflow overview
-----------------

1. Align reads to a reference FASTA with `bwa mem` → produces SAM.
2. Convert SAM to BAM with `samtools view -bS`.
3. Sort BAM with `samtools sort` and index with `samtools index`.
4. Mark duplicates with `picard MarkDuplicates` (write metrics file).
5. Run `samtools flagstat` to produce basic alignment statistics.

Required reference genome files
------------------------------

You need a reference FASTA (for example, a small chromosome like chr20 or chr22). Place the FASTA in `refs/` (e.g., `refs/chr20.fa`). Before alignment, build indexes:

```bash
# BWA index (creates .bwt, .pac, .ann, .amb, .sa files)
bwa index refs/chr20.fa

# Samtools faidx (creates refs/chr20.fa.fai)
samtools faidx refs/chr20.fa

# (Optional) Create a sequence dictionary for Picard
picard CreateSequenceDictionary R=refs/chr20.fa O=refs/chr20.dict
```

Scripts
-------

`run_alignment.sh` — runs `bwa mem` and converts SAM to unsorted BAM.

Usage example:

```bash
# align and produce unsorted BAM
bash scripts/run_alignment.sh refs/chr20.fa data/NA12878_small_R1.fastq.gz results/sample_unsorted.bam -t 4
```

`process_bam.sh` — sorts, indexes, marks duplicates, and runs `flagstat`.

Usage example:

```bash
# sort, mark duplicates, index, and flagstat
bash scripts/process_bam.sh results/sample_unsorted.bam results/processed -t 4
```

Commands to build a BWA index
-----------------------------

As above, run:

```bash
bwa index refs/your_reference.fa
samtools faidx refs/your_reference.fa
picard CreateSequenceDictionary R=refs/your_reference.fa O=refs/your_reference.dict
```

Expected outputs
----------------

- `results/sample_unsorted.bam` — unsorted BAM produced from alignment
- `results/processed/sample.sorted.bam` — sorted BAM
- `results/processed/sample.sorted.bam.bai` — BAM index
- `results/processed/sample.dedup.bam` — duplicates-marked BAM (output from Picard)
- `results/processed/sample.metrics.txt` — Picard duplication metrics
- `results/processed/sample.flagstat.txt` — output from `samtools flagstat`

SAM vs BAM (brief)
------------------

- SAM: Sequence Alignment/Map format — a human-readable, tab-delimited text format describing alignments. Useful for inspection but large on disk.
- BAM: the binary, compressed representation of SAM. Efficient for storage and fast random access when indexed.

Why sorting, indexing, and duplicate marking?
-------------------------------------------

- Sorting: many downstream tools (e.g., variant callers) expect reads sorted by reference coordinate. Sorting groups reads by genomic position, enabling efficient algorithms.
- Indexing: `samtools index` creates an index allowing rapid retrieval of alignments overlapping genomic regions without reading the whole file.
- Duplicate marking: PCR or optical duplicates inflate coverage and can bias variant calling. Marking (and optionally removing) duplicates reduces false positives.

What this implies
-----------------

This module provides the minimal set of commands and scripts needed to transform raw reads into a processed BAM ready for downstream analysis (variant calling, QC). The example uses a tiny demonstration FASTQ and a small reference; for real datasets use full references and scale compute resources accordingly.

Example output (hypothetical)
-----------------------------

```
# samtools flagstat (example, DO NOT treat as real):
100 + 0 in total (QC-passed reads + QC-failed reads)
90 + 0 mapped (90.0% : N/A)
```

Replace `refs/your_reference.fa` and `data/NA12878_small_R1.fastq.gz` with your paths when running locally.

# End-to-End Execution

## Run full pipeline (step-by-step)

1. 01_fastq_qc
2. 02_alignment_bam_processing
3. 03_variant_calling_gatk
4. 04_variant_annotation
5. 05_population_pca
6. 06_asthma_gwas
7. 07_polygenic_risk_score
8. 09_eqtl_mapping

## Run Nextflow pipeline

cd nextflow
nextflow run main.nf
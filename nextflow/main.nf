#!/usr/bin/env nextflow
nextflow.enable.dsl = 2

/*
 * Downstream statistical genetics workflow
 *
 * Flow:
 *   GWAS  →  PRS   (module 07_polygenic_risk_score)
 *   GWAS  →  EQTL  (module 09_gwas_to_eqtl)
 *
 * Calls existing module scripts directly.
 * Analysis logic lives in each module directory — nothing is reimplemented here.
 *
 * Usage (from repo root):
 *   conda activate genomics_pipeline
 *   nextflow run nextflow/main.nf -params-file nextflow/params.json
 *
 * Prerequisites:
 *   Module 05 outputs must exist at 05_population_pca/results/ before running.
 *   See 05_population_pca/README.md for instructions.
 */

// ---------------------------------------------------------------------------
// GWAS — module 06
// Writes all outputs to 06_asthma_gwas/results/ and 06_asthma_gwas/figures/.
// No arguments: run_gwas.sh uses hardcoded relative paths from its directory.
// ---------------------------------------------------------------------------
process GWAS {

    output:
    val "${launchDir}/06_asthma_gwas/results/asthma_gwas.assoc.logistic", emit: assoc_logistic

    script:
    """
    cd "${launchDir}/06_asthma_gwas"
    bash scripts/run_gwas.sh
    """
}

// ---------------------------------------------------------------------------
// PRS — module 07_polygenic_risk_score
// Depends on the .assoc.logistic file produced by GWAS.
// Writes outputs to 07_polygenic_risk_score/results/.
// ---------------------------------------------------------------------------
process PRS {

    input:
    val assoc_logistic

    script:
    """
    cd "${launchDir}/07_polygenic_risk_score"
    bash scripts/run_prs.sh \
        "${launchDir}/${params.geno_prefix}" \
        "${launchDir}/${params.pheno_file}" \
        "${assoc_logistic}" \
        "${launchDir}/${params.prs_out_prefix}" \
        "${params.prs_p_threshold}"
    """
}

// ---------------------------------------------------------------------------
// EQTL — module 09_gwas_to_eqtl
// Depends on the .assoc.logistic file produced by GWAS.
// Writes outputs to 09_gwas_to_eqtl/results/.
// ---------------------------------------------------------------------------
process EQTL {

    input:
    val assoc_logistic

    script:
    """
    cd "${launchDir}/09_gwas_to_eqtl"
    bash scripts/run_eqtl.sh \
        "${assoc_logistic}" \
        "${launchDir}/${params.eqtl_ref}" \
        "${launchDir}/${params.eqtl_out_prefix}" \
        "${params.eqtl_top_n}"
    """
}

// ---------------------------------------------------------------------------
// Workflow entry point
// GWAS runs first; PRS and EQTL branch from its output in parallel.
// ---------------------------------------------------------------------------
workflow {
    gwas_out = GWAS()
    PRS(gwas_out.assoc_logistic)
    EQTL(gwas_out.assoc_logistic)
}

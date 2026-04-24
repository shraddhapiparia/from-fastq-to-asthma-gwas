#!/usr/bin/env Rscript

# Generate Manhattan and QQ plots for GWAS results
# Input: results/asthma_gwas.assoc.logistic
# Output: figures/manhattan_plot.png, figures/qq_plot.png

library(ggplot2)
library(dplyr)

# read.table handles PLINK's leading-space header and variable whitespace robustly
gwas <- read.table("results/asthma_gwas.assoc.logistic", header = TRUE,
                   stringsAsFactors = FALSE) %>%
    filter(TEST == "ADD", !is.na(P))

# Manhattan plot
gwas$CHR <- as.factor(gwas$CHR)
manhattan <- ggplot(gwas, aes(x = BP, y = -log10(P), color = CHR)) +
    geom_point(alpha = 0.6, size = 1) +
    geom_hline(yintercept = -log10(5e-8), linetype = "dashed",
               colour = "red", linewidth = 0.5) +
    scale_color_manual(values = rep(c("#4393C3", "#D6604D"), length(unique(gwas$CHR)))) +
    labs(title = "Manhattan Plot — Toy Asthma GWAS",
         x = "Position",
         y = expression(-log[10](italic(p)))) +
    theme_minimal() +
    theme(legend.position = "none",
          plot.title = element_text(hjust = 0.5))

ggsave("figures/manhattan_plot.png", manhattan, width = 8, height = 4, dpi = 150)

# Genomic inflation factor: median(observed chi-sq) / median(chi-sq(1) distribution)
# Correct formula — NOT the ratio of -log10(p) medians
chisq_obs <- qchisq(gwas$P, df = 1, lower.tail = FALSE)
lambda    <- median(chisq_obs) / qchisq(0.5, df = 1)

# QQ plot
observed <- sort(-log10(gwas$P))
expected <- sort(-log10(ppoints(length(observed))))
qq_data  <- data.frame(expected = expected, observed = observed)

qq_plot <- ggplot(qq_data, aes(x = expected, y = observed)) +
    geom_point(alpha = 0.6) +
    geom_abline(slope = 1, intercept = 0, colour = "red", linetype = "dashed") +
    labs(title = sprintf("QQ Plot — Toy Asthma GWAS  (λ = %.3f)", lambda),
         x = expression("Expected " * -log[10](italic(p))),
         y = expression("Observed " * -log[10](italic(p)))) +
    theme_minimal() +
    theme(plot.title = element_text(hjust = 0.5))

ggsave("figures/qq_plot.png", qq_plot, width = 6, height = 4, dpi = 150)

# Top hits table (all SNPs, sorted by p-value; no threshold cut so the file is never empty)
top_hits <- gwas %>%
    arrange(P) %>%
    head(10) %>%
    select(CHR, SNP, BP, A1, OR, STAT, P)
write.table(top_hits, "results/top_hits.tsv",
            sep = "\t", row.names = FALSE, quote = FALSE)

message(sprintf("Genomic inflation factor λ = %.3f", lambda))
message("Plots saved to figures/")
message("Top hits saved to results/top_hits.tsv")
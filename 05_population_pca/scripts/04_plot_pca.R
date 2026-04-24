#!/usr/bin/env Rscript

# Plot PCA results
# Input: results/demo_genotypes_pca.eigenvec
# Output: figures/pca_plot.png

library(ggplot2)
library(readr)
library(dplyr)

# Read PCA eigenvectors
pca <- read_table("results/demo_genotypes_pca.eigenvec",
                  col_names = c("FID", "IID", paste0("PC", 1:10)))

# Read population labels from fam file (7 cols if simulate_demo_data.sh was run, else 6)
fam_raw <- read_table("../datasets/data/demo_genotypes.fam", col_names = FALSE)
if (ncol(fam_raw) >= 7) {
    fam <- fam_raw %>% select(FID = X1, IID = X2, POP = X7)
} else {
    fam <- fam_raw %>% select(FID = X1, IID = X2) %>% mutate(POP = "Unknown")
}

# Merge PCA with population
pca_plot <- pca %>%
    left_join(fam, by = c("FID", "IID"))

# Calculate variance explained (approximate from eigenvalues)
eigenval <- read_table("results/demo_genotypes_pca.eigenval", col_names = "EIGENVAL")
var_explained <- eigenval$EIGENVAL / sum(eigenval$EIGENVAL) * 100

# Create plot
p <- ggplot(pca_plot, aes(x = PC1, y = PC2, color = POP)) +
    geom_point(alpha = 0.7, size = 2) +
    labs(title = "Principal Component Analysis",
         x = sprintf("PC1 (%.1f%% variance)", var_explained[1]),
         y = sprintf("PC2 (%.1f%% variance)", var_explained[2]),
         color = "Population") +
    theme_minimal() +
    theme(plot.title = element_text(hjust = 0.5))

# Save PCA scatter plot
ggsave("figures/pca_plot.png", p, width = 6, height = 4, dpi = 150)
message("PCA plot saved to figures/pca_plot.png")

# Scree plot
scree_df <- data.frame(
    PC    = factor(paste0("PC", seq_len(nrow(eigenval))), levels = paste0("PC", seq_len(nrow(eigenval)))),
    VarEx = var_explained
)
scree <- ggplot(scree_df, aes(x = PC, y = VarEx)) +
    geom_col(fill = "steelblue") +
    geom_line(aes(group = 1), colour = "black", linewidth = 0.5) +
    geom_point(size = 2) +
    labs(title = "Scree Plot", x = "Principal Component", y = "Variance Explained (%)") +
    theme_minimal() +
    theme(plot.title = element_text(hjust = 0.5))
ggsave("figures/scree_plot.png", scree, width = 6, height = 4, dpi = 150)
message("Scree plot saved to figures/scree_plot.png")
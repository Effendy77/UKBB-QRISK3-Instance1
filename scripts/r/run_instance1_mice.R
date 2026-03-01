# =========================================================
# QRISK3 Instance 1 – Multiple Imputation
# =========================================================

if (!require(mice)) install.packages("mice")
library(mice)

# ---- Paths (portable suggestion) ----
input_file  <- file.path("data", "intermediate", "instance1_qrisk3_ready_v1.csv")
output_file <- file.path("data", "imputed", "instance1_qrisk3_imputed.csv")

if (!file.exists(input_file)) {
  stop("Input file not found: ", input_file)
}

data <- read.csv(input_file)

# ---- Variables to impute ----
mice_vars <- c(
  "cholesterol_HDL_ratio",
  "smoke",
  "weight",
  "height",
  "systolic_blood_pressure",
  "townsend"
)

# ---- Ensure correct types ----
data$smoke <- factor(data$smoke, levels = c(1,2,3,4,5))

# ---- Missingness summary ----
cat("Missingness proportion:\n")
print(colMeans(is.na(data[, mice_vars])))

mice_data <- data[, mice_vars]

# ---- Run MICE ----
set.seed(123)
imp <- mice(mice_data, m = 10, printFlag = FALSE)

# Optional: convergence diagnostic (run once interactively)
# plot(imp)

completed_subset <- complete(imp, 1)

# Replace only imputed columns
data[, mice_vars] <- completed_subset

write.csv(data, output_file, row.names = FALSE)

cat("✅ MICE imputation complete.\n")
cat("Output saved to:", output_file, "\n")
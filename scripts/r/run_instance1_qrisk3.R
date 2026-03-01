# =========================================================
# QRISK3 Instance 1 – Risk Calculation
# =========================================================

if (!require(QRISK3)) install.packages("QRISK3")
library(QRISK3)

# ---- Paths (portable suggestion) ----
input_file  <- file.path("data","imputed","instance1_qrisk3_imputed.csv")
output_file <- file.path("results","risk_outputs","instance1_qrisk3_results.csv")

if (!file.exists(input_file)) {
  stop("Imputed file not found: ", input_file)
}

data <- read.csv(input_file)

# ---- Sanity check ----
required_cols <- c("patid","gender","age","ethnicity","smoke")
missing_cols <- setdiff(required_cols, colnames(data))
if(length(missing_cols) > 0){
  stop("Missing required columns: ", paste(missing_cols, collapse=", "))
}

# ---- Compute QRISK3 ----
qrisk_results <- QRISK3_2017(
  data = data,
  patid = "patid",
  gender = "gender",
  age = "age",
  atrial_fibrillation = "atrial_fibrillation",
  atypical_antipsy = "atypical_antipsy",
  regular_steroid_tablets = "regular_steroid_tablets",
  erectile_dysfunction = "erectile_dysfunction",
  migraine = "migraine",
  rheumatoid_arthritis = "rheumatoid_arthritis",
  chronic_kidney_disease = "chronic_kidney_disease",
  severe_mental_illness = "severe_mental_illness",
  systemic_lupus_erythematosus = "systemic_lupus_erythematosus",
  blood_pressure_treatment = "blood_pressure_treatment",
  diabetes1 = "diabetes1",
  diabetes2 = "diabetes2",
  weight = "weight",
  height = "height",
  ethnicity = "ethnicity",
  heart_attack_relative = "heart_attack_relative",
  cholesterol_HDL_ratio = "cholesterol_HDL_ratio",
  systolic_blood_pressure = "systolic_blood_pressure",
  std_systolic_blood_pressure = "std_systolic_blood_pressure",
  smoke = "smoke",
  townsend = "townsend"
)

write.csv(qrisk_results, output_file, row.names = FALSE)

cat("✅ QRISK3 calculation complete.\n")
cat("Output saved to:", output_file, "\n")
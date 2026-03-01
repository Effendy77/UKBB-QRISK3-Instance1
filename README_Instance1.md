📘 README.md
QRISK3 – Instance 1 Cohort (UK Biobank)
📌 Overview

This repository implements a fully reproducible pipeline for computing 10-year QRISK3 cardiovascular risk scores using UK Biobank Instance 1 baseline data.

This version explicitly uses:

Instance 1 (Assessment Centre baseline visit)
corresponding to the time point aligned with retinal imaging acquisition.

This repository was developed as part of the Retina–Cardio–Renal AI project to enable comparison between:

Deep learning retinal prediction models

Traditional cardiovascular risk estimation (QRISK3)

The pipeline includes:

Structured clinical variable derivation

Disease flag construction

Missing data handling via MICE

Sex-specific QRISK3 calculation in R

Export of risk probabilities for downstream modelling

🧠 Study Context

QRISK3 was calculated to:

Provide benchmark cardiovascular risk estimates

Enable comparison with retinal deep learning predictions

Support hybrid precision medicine modelling

Serve as comparator model in publication

This repository focuses exclusively on:

Instance 1 cohort without prior cardiovascular disease

Temporal alignment is critical — QRISK3 inputs reflect risk at baseline (retinal imaging timepoint).

🗂 Repository Structure (Current Working Version)
INSTANCE-1/
│
├── QRISK3_FULL/                    # Disease-specific flag builders
│
├── build_instance1_base_raw.py
├── build_instance1_master_raw.py
│
├── build_inst1_clinical_layer.py
├── build_inst1_diabetes.py
├── build_inst1_family_history.py
├── build_inst1_hypertension.py
├── build_inst1_smoking.py
│
├── build_inst1_qrisk3_master_v1.py
├── build_inst1_qrisk3_ready.py
│
├── run_instance1_mice.R
├── run_instance1_qrisk3.R
│
├── instance1_qrisk3_results.csv
└── instance1_qrisk3_results.rds
🔬 Pipeline Description
1️⃣ Raw Extraction Layer
build_instance1_base_raw.py

Extracts Instance 1 baseline variables from UK Biobank raw dataset.

Outputs:

instance1_base_raw.csv
2️⃣ Master Raw Construction
build_instance1_master_raw.py

Merges baseline demographic, clinical and laboratory fields into a unified raw dataset.

Outputs:

instance1_master_raw.csv
3️⃣ Clinical Variable Construction

Separate modular scripts generate QRISK3-compatible variables:

Script	Variable Constructed
build_inst1_smoking.py	Smoking category
build_inst1_hypertension.py	Treated hypertension
build_inst1_diabetes.py	Type 2 diabetes
build_inst1_family_history.py	Family history CVD
build_inst1_clinical_layer.py	Combined clinical flags

Each script produces intermediate CSV files.

4️⃣ Disease Flag Construction (QRISK3_FULL)

Contains condition-specific builders:

Atrial fibrillation

CKD

Rheumatoid arthritis

SLE

Severe mental illness

Steroid use

Erectile dysfunction

Atypical antipsychotic use

Treated hypertension (combined)

Each script outputs:

instance1_<condition>.csv

These are merged into the final QRISK3-ready dataset.

5️⃣ MICE Imputation
run_instance1_mice.R

Imputation strategy:

Method: Multiple Imputation by Chained Equations (MICE)

m = 10 imputations

Predictive mean matching for continuous variables

Polytomous/logistic regression for categorical variables

For risk score computation, the first completed dataset was used.

Imputation uncertainty is documented but pooled QRISK3 risk was not applied, as QRISK3 produces deterministic risk estimates.

Output:

instance1_qrisk3_imputed.csv

6️⃣ QRISK3 Computation
run_instance1_qrisk3.R

Uses validated R implementation of QRISK3

Sex-specific equations applied

10-year ASCVD probability calculated

Risk returned as continuous probability (%)

Output:

instance1_qrisk3_results.csv
instance1_qrisk3_results.rds
📊 Cohort Definition

Inclusion:

UK Biobank participants

Instance 1 baseline visit

Available retinal imaging

Complete baseline demographic linkage

Exclusion:

Prevalent cardiovascular disease

Missing critical QRISK3 inputs (handled via MICE)

Final analytic sample size is reported in manuscript.

🧮 QRISK3 Variables Used

Age

Sex

Ethnicity

Townsend deprivation index

Smoking category

Diabetes

Treated hypertension

SBP

SBP variability

Total cholesterol / HDL ratio

BMI

Family history CVD

Atrial fibrillation

CKD

RA

SLE

Severe mental illness

Steroid use

Erectile dysfunction (men)

All variables mapped explicitly to UK Biobank field IDs in manuscript.

⚠️ Important: Variable Naming Compatibility with QRISK3 R Package

The unofficial QRISK3 R implementation (Li et al., 2020) contains known spelling inconsistencies in argument names, including:

ethiniciy (instead of ethnicity)

erectile_disfunction (instead of erectile_dysfunction)

systemic_lupus_erythematosis (instead of systemic_lupus_erythematosus)

To ensure full compatibility with the QRISK3 R function (QRISK3_2017()), this repository preserves the exact argument naming used by the package.

⚠️ These spellings are intentional and required for correct execution of the QRISK3 function.

Renaming these variables without modifying the R function call may result in errors or silent misalignment of inputs.

This design ensures that:

Published results remain reproducible

Risk estimates match those generated in the original analysis

No post-hoc renaming affects calculated probabilities

🔁 Reproducibility
Environment

Python 3.9+

R 4.2+

MICE package

tidyverse

To run full pipeline:

python build_instance1_base_raw.py
python build_instance1_master_raw.py

python build_inst1_clinical_layer.py
python build_inst1_diabetes.py
python build_inst1_hypertension.py
python build_inst1_smoking.py

Rscript run_instance1_mice.R
Rscript run_instance1_qrisk3.R
🔐 Data Governance

⚠️ UK Biobank raw data are not included in this repository.

All intermediate CSV outputs are excluded via .gitignore.

Users must have approved UK Biobank access to reproduce the analysis.

📜 QRISK3 License Notice

QRISK3 algorithm is © ClinRisk Ltd.

This implementation is for academic research use only.

Users must ensure compliance with QRISK3 licensing requirements prior to any clinical or commercial application.

🎯 Intended Use

This repository supports:

Cardiovascular risk benchmarking

Deep learning model comparison

Hybrid multimodal risk prediction research

Reproducible PhD-level methodology

📚 Citation

If used in academic work, please cite:

Effendy Bin Hashim et al. QRISK3 computation in UK Biobank Instance 1 cohort. GitHub repository.
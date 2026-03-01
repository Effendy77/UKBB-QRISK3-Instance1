Variable Derivation Logic – QRISK3 Instance 1
Overview

This document describes the derivation of all QRISK3 input variables from UK Biobank Instance 1 baseline data.

All variables reflect measurements at the time of baseline retinal imaging.

Cohort Definition

UK Biobank participants

Instance 1 (Assessment Centre baseline)

Excluded:

Prevalent cardiovascular disease

Missing critical identifiers

Final analytic sample reported in manuscript

Core Demographic Variables
Age

UKB Field: 21003-1.0

Used directly (years)

Sex

UKB Field: 31

Recoded:

0 = Female

1 = Male

Ethnicity

UKB Field: 21000

Mapped to QRISK3 ethnicity categories

Townsend Deprivation Index

UKB Field: 189-1.0

Used as continuous variable

Blood Pressure
SBP

UKB Fields:

4080-1.0

4080-1.1

Mean of two measurements used

SBP Variability

Standard deviation of available SBP readings at Instance 1.

Lipids
Total Cholesterol

UKB Field: 30690

HDL Cholesterol

UKB Field: 30760

Cholesterol Ratio

Total / HDL

BMI

UKB Field: 21001

Used directly (kg/m²)

Smoking

Derived from:

UKB Field: 20116

Mapped to QRISK3 categories:

0 = Non-smoker

1 = Light

2 = Moderate

3 = Heavy

Clinical Conditions

Each condition constructed via combination of:

Self-reported illness

Hospital episode statistics (ICD codes)

Medication records

Diabetes

Self-report OR HbA1c ≥ 48 mmol/mol

Insulin use considered

Treated Hypertension

Antihypertensive medication use

Atrial Fibrillation

ICD-10 codes I48

Chronic Kidney Disease

eGFR < 60 ml/min/1.73m² OR ICD codes

Rheumatoid Arthritis

ICD-10 M05–M06

Systemic Lupus Erythematosus

ICD-10 M32

Severe Mental Illness

Schizophrenia / Bipolar disorder codes

Steroid Use

Oral glucocorticoid prescriptions

Erectile Dysfunction (men only)

Self-report OR medication

Missing Data Handling

Missing values were addressed using:

Multiple Imputation by Chained Equations (MICE)

m = 5 imputations

Predictive mean matching (continuous)

Logistic regression (binary)

Rubin’s rules used for pooled estimates.

QRISK3 Calculation

R implementation

Sex-specific equations

10-year ASCVD risk probability

Output as continuous %

This derivation logic ensures full reproducibility and transparency.

QRISK3 Variable Naming Alignment

Variable names in the final QRISK3-ready dataset follow the argument structure of the unofficial QRISK3 R implementation (Li et al., 2020), including preserved spelling conventions.

This ensures strict reproducibility of calculated risk probabilities.
import os
import sys
import pandas as pd
import numpy as np

# --------------------------------------------------
# Ensure project root is accessible
# --------------------------------------------------

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)

from config import INTERMEDIATE_DIR

# --------------------------------------------------
# LOAD MASTER DATASET
# --------------------------------------------------

INPUT_PATH = os.path.join(
    INTERMEDIATE_DIR,
    "instance1_master_raw.csv"
)

print("Loading master dataset...")
df = pd.read_csv(INPUT_PATH)

# --------------------------------------------------
# AGE (already computed in base? if not derive)
# --------------------------------------------------

if "age" not in df.columns:
    # fallback if age_at_recruitment exists
    if "21022-0.0" in df.columns:
        df["age"] = pd.to_numeric(df["21022-0.0"], errors="coerce")

# --------------------------------------------------
# HEIGHT / WEIGHT
# --------------------------------------------------

df["height"] = pd.to_numeric(df.get("50-1.0"), errors="coerce")
df["weight"] = pd.to_numeric(df.get("21002-1.0"), errors="coerce")

# --------------------------------------------------
# SBP (mean of available readings)
# --------------------------------------------------

sbp_cols = ['4080-1.0','4080-1.1','93-1.0','93-1.1']
existing_sbp_cols = [c for c in sbp_cols if c in df.columns]

df["systolic_blood_pressure"] = df[existing_sbp_cols].mean(axis=1)
df["std_systolic_blood_pressure"] = df[existing_sbp_cols].std(axis=1)

# --------------------------------------------------
# GENDER (QRISK3 format)
# UKB: 0=female,1=male
# QRISK3: 0=male,1=female
# --------------------------------------------------

df["gender"] = df["31-0.0"].apply(
    lambda x: 0 if x == 1 else 1
)

# --------------------------------------------------
# RENAME PHENOTYPE FLAGS TO QRISK3 FORMAT
# --------------------------------------------------

rename_map = {
    "eid": "patid",
    "af_inst1": "atrial_fibrillation",
    "atypical_antipsy_inst1": "atypical_antipsy",
    "steroid_inst1": "regular_steroid_tablets",
    "erectile_dysfunction_inst1": "erectile_dysfunction",
    "ra_inst1": "rheumatoid_arthritis",
    "ckd_inst1": "chronic_kidney_disease",
    "smi_inst1": "severe_mental_illness",
    "sle_inst1": "systemic_lupus_erythematosus",
    "treated_htn_inst1": "blood_pressure_treatment",
    "fh_cvd": "heart_attack_relative",
    "smoke_cat": "smoke",
    "30690-1.0": "total_cholesterol",
    "30760-1.0": "hdl_cholesterol",
    "21000-0.0": "ethnicity",
    "189-0.0": "townsend"
}

df = df.rename(columns=rename_map)

# --------------------------------------------------
# CHOLESTEROL RATIO
# --------------------------------------------------

df["cholesterol_HDL_ratio"] = (
    df["total_cholesterol"] /
    df["hdl_cholesterol"]
)

# --------------------------------------------------
# ENSURE BINARY FLAGS
# --------------------------------------------------

binary_cols = [
    "atrial_fibrillation",
    "atypical_antipsy",
    "regular_steroid_tablets",
    "erectile_dysfunction",
    "rheumatoid_arthritis",
    "chronic_kidney_disease",
    "severe_mental_illness",
    "systemic_lupus_erythematosus",
    "blood_pressure_treatment",
    "heart_attack_relative"
]

for col in binary_cols:
    if col in df.columns:
        df[col] = df[col].fillna(0).astype(int)

# --------------------------------------------------
# FINAL COLUMN ORDER
# --------------------------------------------------

final_cols = [
    "patid",
    "gender",
    "age",
    "atrial_fibrillation",
    "atypical_antipsy",
    "regular_steroid_tablets",
    "erectile_dysfunction",
    "rheumatoid_arthritis",
    "chronic_kidney_disease",
    "severe_mental_illness",
    "systemic_lupus_erythematosus",
    "blood_pressure_treatment",
    "weight",
    "height",
    "ethnicity",
    "heart_attack_relative",
    "cholesterol_HDL_ratio",
    "systolic_blood_pressure",
    "std_systolic_blood_pressure",
    "smoke",
    "townsend"
]

df_final = df[final_cols]

# --------------------------------------------------
# SAVE
# --------------------------------------------------

OUTPUT_PATH = os.path.join(
    INTERMEDIATE_DIR,
    "instance1_qrisk3_ready_v1.csv"
)

df_final.to_csv(OUTPUT_PATH, index=False)

print("✅ QRISK3 Instance 1 dataset successfully built.")
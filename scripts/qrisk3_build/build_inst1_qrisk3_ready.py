import os
import sys
import pandas as pd
import numpy as np

# --------------------------------------------------
# Use config for portability
# --------------------------------------------------

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)

from config import INTERMEDIATE_DIR

print("Loading master raw dataset...")

INPUT_PATH = os.path.join(INTERMEDIATE_DIR, "instance1_master_raw.csv")
df = pd.read_csv(INPUT_PATH)

# =========================================================
# AGE CALCULATION
# =========================================================

df["34-0.0"] = pd.to_numeric(df["34-0.0"], errors="coerce")

df["instance_year"] = df["53-1.0"].astype(str).str[:4]
df["instance_year"] = pd.to_numeric(df["instance_year"], errors="coerce")

df["age"] = (df["instance_year"] - df["34-0.0"]).astype(float)

# =========================================================
# ANTHROPOMETRY
# =========================================================

df["height"] = pd.to_numeric(df["50-1.0"], errors="coerce")
df["weight"] = pd.to_numeric(df["21002-1.0"], errors="coerce")

# =========================================================
# SBP MEAN + SD (vectorised)
# =========================================================

sbp_cols = ["4080-1.0", "4080-1.1", "93-1.0", "93-1.1"]

for col in sbp_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df["systolic_blood_pressure"] = df[sbp_cols].mean(axis=1)
df["std_systolic_blood_pressure"] = df[sbp_cols].std(axis=1).fillna(0)

# =========================================================
# DIABETES AT INSTANCE 1
# =========================================================

date_cols = ["130706-0.0", "130708-0.0", "130712-0.0", "130714-0.0"]

for col in date_cols:
    df[col] = pd.to_datetime(df[col], errors="coerce", dayfirst=True)

df["diabetes1"] = (
    (df["130706-0.0"].notna()) &
    (df["130706-0.0"] <= df["53-1.0_dt"])
).astype(int)

df["diabetes2"] = (
    (
        df["130708-0.0"].notna() |
        df["130712-0.0"].notna() |
        df["130714-0.0"].notna()
    ) &
    (
        df[["130708-0.0","130712-0.0","130714-0.0"]]
        .min(axis=1) <= df["53-1.0_dt"]
    )
).astype(int)

# =========================================================
# GENDER
# =========================================================

df["31-0.0"] = pd.to_numeric(df["31-0.0"], errors="coerce")
df["gender"] = df["31-0.0"].map({1:0, 0:1})

# =========================================================
# ETHNICITY
# =========================================================

df["21000-0.0"] = pd.to_numeric(df["21000-0.0"], errors="coerce")

eth_map = {
    1001: 1, 1002: 1, 1003: 1,
    2001: 2,
    3001: 3,
    3002: 4,
    3003: 5,
    4001: 6,
    4002: 7,
    5001: 8,
    6001: 9
}

df["ethnicity"] = df["21000-0.0"].map(eth_map).fillna(1).astype(int)

# =========================================================
# CHOLESTEROL RATIO
# =========================================================

df["total_chol"] = pd.to_numeric(df["30690-1.0"], errors="coerce")
df["hdl_chol"]   = pd.to_numeric(df["30760-1.0"], errors="coerce")

df["cholesterol_HDL_ratio"] = df["total_chol"] / df["hdl_chol"]

# =========================================================
# FINAL DATAFRAME
# =========================================================

df_final = pd.DataFrame({
    "patid": df["eid"],
    "gender": df["gender"],
    "age": df["age"],
    "atrial_fibrillation": df["af_inst1"],
    "atypical_antipsy": df["atypical_antipsy_inst1"],
    "regular_steroid_tablets": df["steroid_inst1"],
    "erectile_dysfunction": df["erectile_dysfunction_inst1"],
    "migraine": 0,
    "rheumatoid_arthritis": df["ra_inst1"],
    "chronic_kidney_disease": df["ckd_inst1"],
    "severe_mental_illness": df["smi_inst1"],
    "systemic_lupus_erythematosus": df["sle_inst1"],
    "blood_pressure_treatment": df["treated_htn_inst1"],
    "diabetes1": df["diabetes1"],
    "diabetes2": df["diabetes2"],
    "weight": df["weight"],
    "height": df["height"],
    "ethnicity": df["ethnicity"],
    "heart_attack_relative": df["fh_cvd"],
    "cholesterol_HDL_ratio": df["cholesterol_HDL_ratio"],
    "systolic_blood_pressure": df["systolic_blood_pressure"],
    "std_systolic_blood_pressure": df["std_systolic_blood_pressure"],
    "smoke": df["smoke_cat"],
    "townsend": pd.to_numeric(df["189-0.0"], errors="coerce")
})

OUTPUT_PATH = os.path.join(INTERMEDIATE_DIR, "instance1_qrisk3_ready_v1.csv")
df_final.to_csv(OUTPUT_PATH, index=False)

print("✅ instance1_qrisk3_ready_v1.csv created successfully.")
import os
import sys

# Add project root to Python path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)

from config import INTERMEDIATE_DIR

import pandas as pd
import numpy as np

# =============================
# PATHS
# =============================

from config import RAW_DIR, INTERMEDIATE_DIR

MAIN_PATH = os.path.join(RAW_DIR, "ukb679947.csv")
TOWNSEND_PATH = os.path.join(RAW_DIR, "ukb670300.csv")

HTN_PATH = os.path.join(INTERMEDIATE_DIR, "instance1_hypertension_v2.csv")
DM_PATH  = os.path.join(INTERMEDIATE_DIR, "instance1_diabetes_v2.csv")

# =============================
# LOAD INSTANCE 1 CORE VARIABLES
# =============================

print("Loading Instance 1 core variables...")

use_cols = [
    "eid",
    "53-1.0",          # Instance 1 date
    "21022-0.0",       # age at recruitment (fallback)
    "21001-1.0",       # BMI
    "31-0.0",          # sex
    "20116-1.0",       # smoking
    "21000-0.0",       # ethnicity
    "189-0.0",         # Townsend (if present)
    "4080-1.0",        # SBP
    "30760-1.0",       # HDL
    "30690-1.0"        # Total cholesterol
]

main = pd.read_csv(
    MAIN_PATH,
    usecols=lambda c: c.replace('"','') in use_cols,
    dtype=str
)

main.columns = main.columns.str.replace('"','')

# =============================
# LOAD TOWNSEND FROM ukb670300
# =============================

print("Loading Townsend...")

town = pd.read_csv(
    "/mnt/d/DATA/main_data/csv/ukb670300.csv",
    usecols=["eid", "189-0.0"],
    dtype=str
)

town.columns = town.columns.str.replace('"','')
town["189-0.0"] = pd.to_numeric(town["189-0.0"], errors="coerce")

# Ensure eid is string
town["eid"] = town["eid"].astype(str)
main["eid"] = main["eid"].astype(str)

main = main.merge(town, on="eid", how="left")

# Convert numeric fields
numeric_cols = [
    "21001-1.0",
    "4080-1.0",
    "30760-1.0",
    "30690-1.0",
    "189-0.0"
]

for col in numeric_cols:
    if col in main.columns:
        main[col] = pd.to_numeric(main[col], errors="coerce")

# Convert sex to numeric (0=Female,1=Male if needed)
main["sex"] = pd.to_numeric(main["31-0.0"], errors="coerce")

# Compute cholesterol ratio
main["chol_ratio"] = main["30690-1.0"] / main["30760-1.0"]

# =============================
# LOAD DERIVED FLAGS
# =============================

print("Merging diabetes and hypertension flags...")

htn = pd.read_csv(HTN_PATH, dtype={"eid": str})
dm  = pd.read_csv(DM_PATH, dtype={"eid": str})

main["eid"] = main["eid"].astype(str)
htn["eid"]  = htn["eid"].astype(str)
dm["eid"]   = dm["eid"].astype(str)

clinical = main.merge(htn, on="eid", how="inner")
clinical = clinical.merge(dm, on="eid", how="inner")

# =============================
# CLEAN VARIABLE NAMES FOR QRISK3
# =============================

clinical.rename(columns={
    "21001-1.0": "bmi",
    "4080-1.0": "systolic_bp",
    "chol_ratio": "cholesterol_ratio",
    "189-0.0": "townsend",
    "hypertension_inst1": "hypertension",
    "diabetes_inst1": "diabetes"
}, inplace=True)

# Keep only necessary columns
final_cols = [
    "eid",
    "sex",
    "bmi",
    "systolic_bp",
    "cholesterol_ratio",
    "townsend",
    "hypertension",
    "diabetes",
    "20116-1.0"   # smoking
]

clinical_final = clinical[final_cols].copy()

clinical_final.rename(columns={
    "20116-1.0": "smoking"
}, inplace=True)

print("\nClinical layer preview:")
print(clinical_final.head())
   
print("\nMissingness summary:")
print(clinical_final.isna().mean())

# =============================
# SAVE
# =============================

OUTPUT_PATH = os.path.join(INTERMEDIATE_DIR, "instance1_clinical_layer.csv")
clinical_final.to_csv(OUTPUT_PATH, index=False)

print("\nSaved instance1_clinical_layer.csv")
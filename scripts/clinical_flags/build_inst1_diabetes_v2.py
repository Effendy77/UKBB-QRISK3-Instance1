import os
import sys

# Add project root to Python path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)

from config import RAW_DIR, INTERMEDIATE_DIR

import pandas as pd
import numpy as np

# =============================
# PATHS
# =============================

MAIN_PATH    = os.path.join(RAW_DIR, "ukb679947.csv")
ICD_PATH     = os.path.join(RAW_DIR, "ukb670300.csv")
DERIVED_PATH = os.path.join(RAW_DIR, "ukb676790.csv")

# =============================
# LOAD INSTANCE 1 DATES
# =============================

print("Loading Instance 1 dates...")

inst1 = pd.read_csv(
    MAIN_PATH,
    usecols=["eid", "53-1.0"],
    dtype=str
)

inst1.columns = inst1.columns.str.replace('"','')
inst1["53-1.0_dt"] = pd.to_datetime(inst1["53-1.0"], errors="coerce")

inst1_cohort = inst1[inst1["53-1.0_dt"].notna()].copy()

print("Instance 1 participants:", len(inst1_cohort))


# =============================
# LOAD DERIVED (ALGORITHMIC) DIABETES
# =============================

print("Loading algorithmic diabetes dates...")

derived = pd.read_csv(
    DERIVED_PATH,
    usecols=[
        "eid",
        "130706-0.0",  # T1D date
        "130708-0.0",  # T2D date
        "130712-0.0",
        "130714-0.0"
    ],
    dtype=str
)

derived.columns = derived.columns.str.replace('"','')

# Convert UK format dates properly (IMPORTANT FIX)
for col in ["130706-0.0","130708-0.0","130712-0.0","130714-0.0"]:
    derived[col] = pd.to_datetime(
        derived[col],
        errors="coerce",
        dayfirst=True   # <-- CRITICAL FIX
    )

# Restrict to Instance 1 cohort
derived = derived.merge(
    inst1_cohort[["eid", "53-1.0_dt"]],
    on="eid",
    how="inner"
)

# Earliest algorithmic diabetes date
derived["dm_algo_date"] = derived[
    ["130706-0.0","130708-0.0","130712-0.0","130714-0.0"]
].min(axis=1)

derived["dm_algo_inst1"] = (
    (derived["dm_algo_date"].notna()) &
    (derived["dm_algo_date"] <= derived["53-1.0_dt"])
).astype(int)

print("Algorithmic diabetes prevalence:",
      derived["dm_algo_inst1"].mean())


# =============================
# LOAD ICD DIABETES
# =============================

print("Loading ICD diabetes...")

with open(ICD_PATH, "r") as f:
    header = f.readline().strip().replace('"','').split(",")

icd10_code_cols = [c for c in header if c.startswith("41270-")]
icd10_date_cols = [c for c in header if c.startswith("41280-")]
icd9_code_cols  = [c for c in header if c.startswith("41271-")]
icd9_date_cols  = [c for c in header if c.startswith("41281-")]

use_cols = ["eid"] + icd10_code_cols + icd10_date_cols + icd9_code_cols + icd9_date_cols

icd = pd.read_csv(ICD_PATH, usecols=use_cols, dtype=str)
icd.columns = icd.columns.str.replace('"','')

# Restrict to Instance 1 participants
icd = icd[icd["eid"].isin(inst1_cohort["eid"])].copy()
icd = icd.merge(
    inst1_cohort[["eid", "53-1.0_dt"]],
    on="eid",
    how="inner"
)

# Convert ICD date columns
for col in icd10_date_cols:
    icd[col] = pd.to_datetime(icd[col], errors="coerce")

for col in icd9_date_cols:
    icd[col] = pd.to_datetime(icd[col], errors="coerce")

icd["dm_icd_inst1"] = 0

# ICD10 E10–E14
for code_col in icd10_code_cols:
    date_col = code_col.replace("41270", "41280")

    mask = (
        icd[code_col].notna() &
        icd[code_col].astype(str).str.startswith(("E10","E11","E12","E13","E14")) &
        (icd[date_col] <= icd["53-1.0_dt"])
    )

    icd.loc[mask, "dm_icd_inst1"] = 1

# ICD9 250
for code_col in icd9_code_cols:
    date_col = code_col.replace("41271", "41281")

    mask = (
        icd[code_col].notna() &
        icd[code_col].astype(str).str.startswith("250") &
        (icd[date_col] <= icd["53-1.0_dt"])
    )

    icd.loc[mask, "dm_icd_inst1"] = 1

print("ICD diabetes prevalence:",
      icd["dm_icd_inst1"].mean())


# =============================
# FINAL MERGE
# =============================

final = derived[["eid","dm_algo_inst1"]].merge(
    icd[["eid","dm_icd_inst1"]],
    on="eid",
    how="inner"
)

final["diabetes_inst1"] = np.where(
    (final["dm_algo_inst1"] == 1) |
    (final["dm_icd_inst1"] == 1),
    1, 0
)

print("\nFinal Diabetes counts:")
print(final["diabetes_inst1"].value_counts())

print("\nFinal Diabetes prevalence:")
print(final["diabetes_inst1"].mean())


# =============================
# SAVE OUTPUT
# =============================

OUTPUT_PATH = os.path.join(INTERMEDIATE_DIR, "instance1_diabetes_v2.csv")

final[["eid","diabetes_inst1"]].to_csv(
    OUTPUT_PATH,
    index=False
)

print("\nSaved instance1_diabetes_v2.csv")
import os
import sys

# --------------------------------------------------
# Ensure project root is accessible
# --------------------------------------------------
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)

from config import RAW_DIR, INTERMEDIATE_DIR

import pandas as pd
import numpy as np

# --------------------------------------------------
# PATHS (Portable)
# --------------------------------------------------

MAIN_PATH = os.path.join(RAW_DIR, "ukb679947.csv")
ICD_PATH  = os.path.join(RAW_DIR, "ukb670300.csv")

# --------------------------------------------------
# LOAD INSTANCE 1 DATES
# --------------------------------------------------

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

# --------------------------------------------------
# LOAD ICD HEADER
# --------------------------------------------------

with open(ICD_PATH, "r") as f:
    icd_header = f.readline().strip().replace('"','').split(",")

icd10_code_cols = [c for c in icd_header if c.startswith("41270-")]
icd10_date_cols = [c for c in icd_header if c.startswith("41280-")]
icd9_code_cols  = [c for c in icd_header if c.startswith("41271-")]
icd9_date_cols  = [c for c in icd_header if c.startswith("41281-")]

use_cols = ["eid"] + icd10_code_cols + icd10_date_cols + icd9_code_cols + icd9_date_cols

print("Loading ICD data...")

icd = pd.read_csv(ICD_PATH, usecols=use_cols, dtype=str)
icd.columns = icd.columns.str.replace('"','')

# Restrict to Instance 1 cohort
icd = icd[icd["eid"].isin(inst1_cohort["eid"])].copy()
icd = icd.merge(inst1_cohort[["eid", "53-1.0_dt"]], on="eid", how="inner")

# --------------------------------------------------
# Convert ICD date columns
# --------------------------------------------------

for col in icd10_date_cols:
    icd[col] = pd.to_datetime(icd[col], errors="coerce")

for col in icd9_date_cols:
    icd[col] = pd.to_datetime(icd[col], errors="coerce")

# --------------------------------------------------
# ICD HYPERTENSION FLAG
# --------------------------------------------------

icd["htn_icd"] = 0

# ICD10: I10–I15
for code_col in icd10_code_cols:
    date_col = code_col.replace("41270", "41280")

    mask = (
        icd[code_col].notna() &
        icd[code_col].astype(str).str.startswith(("I10","I11","I12","I13","I15")) &
        (icd[date_col] <= icd["53-1.0_dt"])
    )

    icd.loc[mask, "htn_icd"] = 1

# ICD9: 401–405
for code_col in icd9_code_cols:
    date_col = code_col.replace("41271", "41281")

    mask = (
        icd[code_col].notna() &
        icd[code_col].astype(str).str.startswith(("401","402","403","404","405")) &
        (icd[date_col] <= icd["53-1.0_dt"])
    )

    icd.loc[mask, "htn_icd"] = 1

print("ICD hypertension prevalence:", icd["htn_icd"].mean())

# --------------------------------------------------
# SELF-REPORT HYPERTENSION (FIELD 20002)
# --------------------------------------------------

with open(MAIN_PATH, "r") as f:
    main_header = f.readline().strip().replace('"','').split(",")

selfrep_cols = ["eid"] + [c for c in main_header if c.startswith("20002-")]

print("Loading self-report data...")

selfrep = pd.read_csv(
    MAIN_PATH,
    usecols=selfrep_cols,
    dtype=str
)

selfrep.columns = selfrep.columns.str.replace('"','')
selfrep = selfrep[selfrep["eid"].isin(inst1_cohort["eid"])].copy()

# Self-report hypertension code = 1065
selfrep["htn_self"] = (
    selfrep.filter(like="20002")
    .isin(["1065"])
    .any(axis=1)
    .astype(int)
)

print("Self-report hypertension prevalence:", selfrep["htn_self"].mean())

# --------------------------------------------------
# MERGE ICD + SELF REPORT
# --------------------------------------------------

icd = icd.merge(
    selfrep[["eid", "htn_self"]],
    on="eid",
    how="left"
)

icd["htn_self"] = icd["htn_self"].fillna(0)

# --------------------------------------------------
# FINAL FLAG
# --------------------------------------------------

icd["hypertension_inst1"] = np.where(
    (icd["htn_icd"] == 1) |
    (icd["htn_self"] == 1),
    1, 0
)

print("\nFinal Hypertension v2 counts:")
print(icd["hypertension_inst1"].value_counts())
print("Final prevalence:", icd["hypertension_inst1"].mean())

# --------------------------------------------------
# SAVE OUTPUT (Portable)
# --------------------------------------------------

OUTPUT_PATH = os.path.join(
    INTERMEDIATE_DIR,
    "instance1_hypertension_v2.csv"
)

icd[["eid", "hypertension_inst1"]].to_csv(
    OUTPUT_PATH,
    index=False
)

print(f"\nSaved to: {OUTPUT_PATH}")
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

from config import RAW_DIR, INTERMEDIATE_DIR

# --------------------------------------------------
# PATHS (Portable)
# --------------------------------------------------

MAIN_PATH = os.path.join(RAW_DIR, "ukb679947.csv")
ICD_PATH  = os.path.join(RAW_DIR, "ukb670300.csv")

print("Loading Instance 1 cohort...")

# =====================================================
# LOAD INSTANCE 1 DATE
# =====================================================

inst1 = pd.read_csv(
    MAIN_PATH,
    usecols=["eid", "53-1.0"],
    dtype=str
)

inst1.columns = inst1.columns.str.replace('"','')
inst1["53-1.0_dt"] = pd.to_datetime(inst1["53-1.0"], errors="coerce")
inst1 = inst1[inst1["53-1.0_dt"].notna()].copy()

print("Instance 1 participants:", len(inst1))

# =====================================================
# LOAD SELF-REPORT + MEDS
# =====================================================

print("Loading self-report + medication data...")

with open(MAIN_PATH, "r") as f:
    header = f.readline().strip().replace('"','').split(",")

sr_cols  = [c for c in header if c.startswith("20002-0.")]
med_cols = [c for c in header if c.startswith("20003-1.")]

use_cols = ["eid"] + sr_cols + med_cols

sr = pd.read_csv(MAIN_PATH, usecols=use_cols, dtype=str)
sr.columns = sr.columns.str.replace('"','')
sr = sr[sr["eid"].isin(inst1["eid"])].copy()

# Convert medication columns to numeric
for col in med_cols:
    sr[col] = pd.to_numeric(sr[col], errors="coerce")

# -----------------------------
# ED CODES
# -----------------------------

ed_diag_code = "1518"

ed_meds_codes = [
    1141168936, 1141168948, 1141168944,
    1141168946, 1140869100, 1140883010
]

# -----------------------------
# VECTORISED SELF + MED FLAG
# -----------------------------

diag_flag = (
    sr[sr_cols]
    .isin([ed_diag_code])
    .any(axis=1)
)

med_flag = (
    sr[med_cols]
    .isin(ed_meds_codes)
    .any(axis=1)
)

sr["ed_self_med"] = (diag_flag | med_flag).astype(int)

# =====================================================
# LOAD ICD DATA
# =====================================================

print("Loading ICD data...")

with open(ICD_PATH, "r") as f:
    icd_header = f.readline().strip().replace('"','').split(",")

icd10_code_cols = [c for c in icd_header if c.startswith("41270-")]
icd10_date_cols = [c for c in icd_header if c.startswith("41280-")]
icd9_code_cols  = [c for c in icd_header if c.startswith("41271-")]
icd9_date_cols  = [c for c in icd_header if c.startswith("41281-")]

use_cols = ["eid"] + icd10_code_cols + icd10_date_cols + icd9_code_cols + icd9_date_cols

icd = pd.read_csv(ICD_PATH, usecols=use_cols, dtype=str)
icd.columns = icd.columns.str.replace('"','')
icd = icd[icd["eid"].isin(inst1["eid"])].copy()

icd = icd.merge(inst1[["eid","53-1.0_dt"]], on="eid", how="inner")

# Convert ICD date columns
for col in icd10_date_cols:
    icd[col] = pd.to_datetime(icd[col], errors="coerce")

for col in icd9_date_cols:
    icd[col] = pd.to_datetime(icd[col], errors="coerce")

# -----------------------------
# ICD ED FLAG
# -----------------------------

icd["ed_icd"] = 0

# ICD-10: N48.4
for code_col in icd10_code_cols:
    date_col = code_col.replace("41270","41280")

    mask = (
        icd[code_col].notna() &
        icd[code_col].astype(str).str.startswith("N484") &
        (icd[date_col] <= icd["53-1.0_dt"])
    )

    icd.loc[mask, "ed_icd"] = 1

# ICD-9: 60784
for code_col in icd9_code_cols:
    date_col = code_col.replace("41271","41281")

    mask = (
        icd[code_col].notna() &
        icd[code_col].astype(str).str.startswith("60784") &
        (icd[date_col] <= icd["53-1.0_dt"])
    )

    icd.loc[mask, "ed_icd"] = 1

# =====================================================
# FINAL MERGE
# =====================================================

final = sr[["eid","ed_self_med"]].merge(
    icd[["eid","ed_icd"]],
    on="eid",
    how="left"
)

final["erectile_dysfunction_inst1"] = (
    final["ed_self_med"].fillna(0) |
    final["ed_icd"].fillna(0)
).astype(int)

print("\nED prevalence at Instance 1:")
print(final["erectile_dysfunction_inst1"].value_counts())
print("Prevalence:", final["erectile_dysfunction_inst1"].mean())

# =====================================================
# SAVE (Portable)
# =====================================================

OUTPUT_PATH = os.path.join(
    INTERMEDIATE_DIR,
    "instance1_ed.csv"
)

final[["eid","erectile_dysfunction_inst1"]].to_csv(
    OUTPUT_PATH,
    index=False
)

print(f"Saved to: {OUTPUT_PATH}")
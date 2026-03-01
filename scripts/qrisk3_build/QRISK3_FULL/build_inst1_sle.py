import os
import sys
import pandas as pd

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

print("Loading Instance 1 dates...")

# --------------------------------------------------
# LOAD INSTANCE 1 DATE
# --------------------------------------------------

inst1 = pd.read_csv(
    MAIN_PATH,
    usecols=["eid", "53-1.0"],
    dtype=str
)

inst1.columns = inst1.columns.str.replace('"','')
inst1["53-1.0_dt"] = pd.to_datetime(inst1["53-1.0"], errors="coerce")
inst1 = inst1[inst1["53-1.0_dt"].notna()].copy()

print("Instance 1 participants:", len(inst1))

# --------------------------------------------------
# LOAD ICD HEADER
# --------------------------------------------------

with open(ICD_PATH, "r") as f:
    header = f.readline().strip().replace('"','').split(",")

icd10_code_cols = [c for c in header if c.startswith("41270-")]
icd10_date_cols = [c for c in header if c.startswith("41280-")]
icd9_code_cols  = [c for c in header if c.startswith("41271-")]
icd9_date_cols  = [c for c in header if c.startswith("41281-")]

use_cols = ["eid"] + icd10_code_cols + icd10_date_cols + icd9_code_cols + icd9_date_cols

print("Loading ICD data...")

icd = pd.read_csv(ICD_PATH, usecols=use_cols, dtype=str)
icd.columns = icd.columns.str.replace('"','')

icd = icd[icd["eid"].isin(inst1["eid"])].copy()
icd = icd.merge(inst1[["eid","53-1.0_dt"]], on="eid", how="inner")

# Convert date columns
for col in icd10_date_cols:
    icd[col] = pd.to_datetime(icd[col], errors="coerce")

for col in icd9_date_cols:
    icd[col] = pd.to_datetime(icd[col], errors="coerce")

# --------------------------------------------------
# COMPUTE SLE FLAG
# --------------------------------------------------

print("Computing SLE_inst1...")

icd = icd.copy()
icd["sle_inst1"] = 0

# ICD10: M32
for code_col in icd10_code_cols:
    date_col = code_col.replace("41270","41280")

    mask = (
        icd[code_col].notna() &
        icd[code_col].astype(str).str.startswith("M32") &
        (icd[date_col] <= icd["53-1.0_dt"])
    )

    icd.loc[mask, "sle_inst1"] = 1

# ICD9: 7100
for code_col in icd9_code_cols:
    date_col = code_col.replace("41271","41281")

    mask = (
        icd[code_col].notna() &
        icd[code_col].astype(str).str.startswith("7100") &
        (icd[date_col] <= icd["53-1.0_dt"])
    )

    icd.loc[mask, "sle_inst1"] = 1

print("\nSLE prevalence at Instance 1:")
print(icd["sle_inst1"].value_counts())
print("Prevalence:", icd["sle_inst1"].mean())

# --------------------------------------------------
# SAVE (Portable)
# --------------------------------------------------

OUTPUT_PATH = os.path.join(
    INTERMEDIATE_DIR,
    "instance1_sle.csv"
)

icd[["eid","sle_inst1"]].to_csv(
    OUTPUT_PATH,
    index=False
)

print(f"Saved to: {OUTPUT_PATH}")
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
# PATH (Portable)
# --------------------------------------------------

MAIN_PATH = os.path.join(RAW_DIR, "ukb679947.csv")

print("Loading Instance 1 dates...")

# -------------------------
# Load Instance 1 attendance
# -------------------------

inst1 = pd.read_csv(
    MAIN_PATH,
    usecols=["eid", "53-1.0"],
    dtype=str
)

inst1.columns = inst1.columns.str.replace('"','')
inst1["53-1.0_dt"] = pd.to_datetime(inst1["53-1.0"], errors="coerce")
inst1 = inst1[inst1["53-1.0_dt"].notna()].copy()

print("Instance 1 participants:", len(inst1))

# -------------------------
# Identify 20003-1.* columns only
# -------------------------

with open(MAIN_PATH, "r") as f:
    header = f.readline().strip().replace('"','').split(",")

med_cols = [c for c in header if c.startswith("20003-1.")]
use_cols = ["eid"] + med_cols

print("Loading medication data...")

df = pd.read_csv(MAIN_PATH, usecols=use_cols, dtype=str)
df.columns = df.columns.str.replace('"','')

df = df[df["eid"].isin(inst1["eid"])].copy()

# Convert medication codes to numeric
for col in med_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# -------------------------
# Atypical antipsychotic codes
# -------------------------

atypical_codes = [
    1140862046,  # Olanzapine
    1140862084,  # Risperidone
    1140862048,  # Quetiapine
    1140862028,  # Aripiprazole
    1140861992,  # Clozapine
    1140861926,  # Amisulpride
    1140862120,  # Sulpiride
    1140862042,  # Paliperidone
    1140862012,  # Lurasidone
    1140862144   # Ziprasidone
]

print("Computing atypical_antipsy_inst1...")

# Vectorized version (fast)
df["atypical_antipsy_inst1"] = (
    df[med_cols]
    .isin(atypical_codes)
    .any(axis=1)
    .astype(int)
)

print("\nAtypical antipsychotic use at Instance 1:")
print(df["atypical_antipsy_inst1"].value_counts())
print("Prevalence:", df["atypical_antipsy_inst1"].mean())

# -------------------------
# SAVE (Portable)
# -------------------------

OUTPUT_PATH = os.path.join(
    INTERMEDIATE_DIR,
    "instance1_atypical_antipsy.csv"
)

df[["eid","atypical_antipsy_inst1"]].to_csv(
    OUTPUT_PATH,
    index=False
)

print(f"Saved to: {OUTPUT_PATH}")
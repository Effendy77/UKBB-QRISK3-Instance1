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

steroid_cols = [c for c in header if c.startswith("20003-1.")]
use_cols = ["eid"] + steroid_cols

print("Loading medication data...")

df = pd.read_csv(MAIN_PATH, usecols=use_cols, dtype=str)
df.columns = df.columns.str.replace('"','')

df = df[df["eid"].isin(inst1["eid"])].copy()

# Convert medication codes to numeric
for col in steroid_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# -------------------------
# Corticosteroid codes
# -------------------------

steroid_codes = [
    1140874790,  # Prednisolone
    1140874816,  # Betamethasone
    1140874896,  # Cortisone
    1140874930,  # Depo-medrone
    1140874976,  # Dexamethasone
    1141145782,  # Deflazacort
    1141173346   # Efcortesol
]

print("Computing steroid_inst1...")

# Vectorized version (fast)
df["steroid_inst1"] = (
    df[steroid_cols]
    .isin(steroid_codes)
    .any(axis=1)
    .astype(int)
)

print("\nSteroid use at Instance 1:")
print(df["steroid_inst1"].value_counts())
print("Prevalence:", df["steroid_inst1"].mean())

# -------------------------
# SAVE (Portable)
# -------------------------

OUTPUT_PATH = os.path.join(
    INTERMEDIATE_DIR,
    "instance1_steroid.csv"
)

df[["eid","steroid_inst1"]].to_csv(
    OUTPUT_PATH,
    index=False
)

print(f"Saved to: {OUTPUT_PATH}")
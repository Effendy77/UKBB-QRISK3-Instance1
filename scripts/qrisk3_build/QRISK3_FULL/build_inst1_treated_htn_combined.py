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
# Identify relevant columns
# -------------------------

with open(MAIN_PATH, "r") as f:
    header = f.readline().strip().replace('"','').split(",")

bp20003_cols = [c for c in header if c.startswith("20003-1.")]
female_bp_cols = [c for c in header if c.startswith("6153-1.")]
male_bp_cols   = [c for c in header if c.startswith("6177-1.")]

use_cols = ["eid", "31-0.0"] + bp20003_cols + female_bp_cols + male_bp_cols

print("Loading medication + self-report data...")

df = pd.read_csv(MAIN_PATH, usecols=use_cols, dtype=str)
df.columns = df.columns.str.replace('"','')

df = df[df["eid"].isin(inst1["eid"])].copy()

# Convert sex
df["31-0.0"] = pd.to_numeric(df["31-0.0"], errors="coerce")

# Convert medication codes
for col in bp20003_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Convert self-report
for col in female_bp_cols + male_bp_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# -------------------------
# Antihypertensive codes
# -------------------------

bp_med_codes = [
    1140860192, 1140860292, 1140860696, 1140860728, 1140860750, 1140860806, 1140860882,
    1140860904, 1140861088, 1140861190, 1140861276, 1140866072, 1140866078, 1140866090,
    1140866102, 1140866108, 1140866122, 1140866138, 1140866156, 1140866162, 1140866724,
    1140866738, 1140868618, 1140872568, 1140874706, 1140874744, 1140875808, 1140879758,
    1140879760, 1140879762, 1140879802, 1140879806, 1140879810, 1140879818, 1140879822,
    1140879826, 1140879830, 1140879834, 1140879842, 1140879866, 1140884298, 1140888552,
    1140888556, 1140888560, 1140888646, 1140909706, 1140910442, 1140910614, 1140916356,
    1140923272, 1140923336, 1140923404, 1140923712, 1140926778, 1140928226, 1141145660,
    1141146126, 1141152998, 1141153026, 1141164276, 1141165470, 1141166006, 1141169516,
    1141171336, 1141180592, 1141180772, 1141180778, 1141184722, 1141193282, 1141194794,
    1141194810
]

print("Computing treated_htn_inst1...")

# -------------------------
# 1. Medication flag (vectorized)
# -------------------------

med_flag = (
    df[bp20003_cols]
    .isin(bp_med_codes)
    .any(axis=1)
)

# -------------------------
# 2. Self-report flag (vectorized, sex-specific)
# -------------------------

female_flag = (
    (df["31-0.0"] == 0) &
    df[female_bp_cols].eq(2).any(axis=1)
)

male_flag = (
    (df["31-0.0"] == 1) &
    df[male_bp_cols].eq(2).any(axis=1)
)

self_flag = female_flag | male_flag

# -------------------------
# Final flag
# -------------------------

df["treated_htn_inst1"] = (med_flag | self_flag).astype(int)

print("\nTreated Hypertension at Instance 1:")
print(df["treated_htn_inst1"].value_counts())
print("Prevalence:", df["treated_htn_inst1"].mean())

# -------------------------
# SAVE (Portable)
# -------------------------

OUTPUT_PATH = os.path.join(
    INTERMEDIATE_DIR,
    "instance1_treated_htn_combined.csv"
)

df[["eid","treated_htn_inst1"]].to_csv(
    OUTPUT_PATH,
    index=False
)

print(f"Saved to: {OUTPUT_PATH}")
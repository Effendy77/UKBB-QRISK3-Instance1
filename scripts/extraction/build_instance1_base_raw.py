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

# --------------------------------------------------
# PATHS (Portable)
# --------------------------------------------------

MAIN_PATH    = os.path.join(RAW_DIR, "ukb679947.csv")
ICD_PATH     = os.path.join(RAW_DIR, "ukb670300.csv")
DERIVED_PATH = os.path.join(RAW_DIR, "ukb676790.csv")

print("Loading Instance 1 assessment fields...")

# =============================
# MAIN ASSESSMENT FILE
# =============================

main_cols = [
    "eid",
    "31-0.0",
    "34-0.0",
    "52-0.0",
    "53-1.0",
    "50-1.0",
    "21002-1.0",
    "4080-1.0",
    "4080-1.1",
    "93-1.0",
    "93-1.1",
    "21000-0.0",
    "30690-1.0",
    "30760-1.0",
    "20107-0.0",
    "20110-0.0",
    "20111-0.0",
    "20116-0.0",
    "20161-0.0"
]

main = pd.read_csv(
    MAIN_PATH,
    usecols=main_cols,
    dtype=str
)

main.columns = main.columns.str.replace('"','')

# Restrict to Instance 1 participants
main["53-1.0_dt"] = pd.to_datetime(main["53-1.0"], errors="coerce")
main = main[main["53-1.0_dt"].notna()].copy()

print("Instance 1 participants:", len(main))

# =============================
# LOAD TOWNSEND
# =============================

print("Loading Townsend from ICD file...")

townsend = pd.read_csv(
    ICD_PATH,
    usecols=["eid", "189-0.0"],
    dtype=str
)

townsend.columns = townsend.columns.str.replace('"','')

# =============================
# LOAD DERIVED DIABETES DATES
# =============================

print("Loading diabetes date fields...")

derived_cols = [
    "eid",
    "130706-0.0",
    "130708-0.0",
    "130712-0.0",
    "130714-0.0"
]

derived = pd.read_csv(
    DERIVED_PATH,
    usecols=derived_cols,
    dtype=str
)

derived.columns = derived.columns.str.replace('"','')

# =============================
# MERGE ALL BASE COMPONENTS
# =============================

base = main.merge(townsend, on="eid", how="left")
base = base.merge(derived, on="eid", how="left")

# =============================
# SAVE (Portable)
# =============================

OUTPUT_PATH = os.path.join(
    INTERMEDIATE_DIR,
    "instance1_base_raw.csv"
)

base.to_csv(OUTPUT_PATH, index=False)

print(f"✅ instance1_base_raw.csv created successfully at: {OUTPUT_PATH}")
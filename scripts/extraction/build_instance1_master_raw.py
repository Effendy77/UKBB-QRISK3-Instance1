import os
import sys
from functools import reduce
import pandas as pd

# --------------------------------------------------
# Ensure project root is accessible
# --------------------------------------------------

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)

from config import INTERMEDIATE_DIR

print("Loading base raw dataset...")

BASE_PATH = os.path.join(INTERMEDIATE_DIR, "instance1_base_raw.csv")
base = pd.read_csv(BASE_PATH)

# =========================================================
# LOAD ALL CONDITION FLAGS
# =========================================================

flag_files = [
    "instance1_af.csv",
    "instance1_ckd.csv",
    "instance1_ra.csv",
    "instance1_sle.csv",
    "instance1_smi.csv",
    "instance1_steroid.csv",
    "instance1_atypical_antipsy.csv",
    "instance1_treated_htn_combined.csv",
    "instance1_ed.csv"
]

print("Loading condition flags...")

flag_dfs = [
    pd.read_csv(os.path.join(INTERMEDIATE_DIR, f))
    for f in flag_files
]

flags_merged = reduce(
    lambda left, right: pd.merge(left, right, on="eid", how="left"),
    flag_dfs
)

# =========================================================
# LOAD SMOKING + FAMILY HISTORY
# =========================================================

print("Loading smoking + family history...")

smoke = pd.read_csv(
    os.path.join(INTERMEDIATE_DIR, "instance1_smoke_cat.csv")
)

fh = pd.read_csv(
    os.path.join(INTERMEDIATE_DIR, "instance1_family_history.csv")
)

# =========================================================
# MERGE EVERYTHING
# =========================================================

print("Merging all components...")

master = base.merge(flags_merged, on="eid", how="left")
master = master.merge(smoke, on="eid", how="left")
master = master.merge(fh, on="eid", how="left")

# =========================================================
# FILL BINARY NAs WITH 0
# =========================================================

binary_cols = [
    "af_inst1",
    "ckd_inst1",
    "ra_inst1",
    "sle_inst1",
    "smi_inst1",
    "steroid_inst1",
    "atypical_antipsy_inst1",
    "treated_htn_inst1",
    "erectile_dysfunction_inst1",
    "fh_cvd"
]

for col in binary_cols:
    if col in master.columns:
        master[col] = master[col].fillna(0).astype(int)

print("\nMaster dataset shape:", master.shape)

# =========================================================
# SAVE (Portable)
# =========================================================

OUTPUT_PATH = os.path.join(
    INTERMEDIATE_DIR,
    "instance1_master_raw.csv"
)

master.to_csv(OUTPUT_PATH, index=False)

print(f"✅ instance1_master_raw.csv created successfully at: {OUTPUT_PATH}")
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

from config import INTERMEDIATE_DIR

# --------------------------------------------------
# PATH (Portable)
# --------------------------------------------------

BASE_PATH = os.path.join(
    INTERMEDIATE_DIR,
    "instance1_base_raw.csv"
)

print("Loading base raw dataset...")
df = pd.read_csv(BASE_PATH)

# Convert smoking fields to numeric
df["20116-0.0"] = pd.to_numeric(df["20116-0.0"], errors="coerce")
df["20161-0.0"] = pd.to_numeric(df["20161-0.0"], errors="coerce")

status = df["20116-0.0"]
pack_years = df["20161-0.0"]

# --------------------------------------------------
# Vectorized smoking classification
# --------------------------------------------------

smoke_cat = pd.Series(np.nan, index=df.index)

# Never smoker
smoke_cat.loc[status == 0] = 1

# Ex-smoker
smoke_cat.loc[status == 1] = 2

# Current smoker
current_mask = (status == 2)

smoke_cat.loc[current_mask & (
    pack_years.isna() | (pack_years < 10)
)] = 3

smoke_cat.loc[current_mask & (
    (pack_years >= 10) & (pack_years < 20)
)] = 4

smoke_cat.loc[current_mask & (
    pack_years >= 20
)] = 5

df["smoke_cat"] = smoke_cat

df_out = df[["eid","smoke_cat"]].copy()

# --------------------------------------------------
# SAVE (Portable)
# --------------------------------------------------

OUTPUT_PATH = os.path.join(
    INTERMEDIATE_DIR,
    "instance1_smoke_cat.csv"
)

df_out.to_csv(OUTPUT_PATH, index=False)

print("Smoking distribution:")
print(df_out["smoke_cat"].value_counts(dropna=False))
print(f"Saved to: {OUTPUT_PATH}")
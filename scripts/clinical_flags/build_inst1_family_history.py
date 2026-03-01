import os
import sys
import pandas as pd

# --------------------------------------------------
# Ensure project root is accessible
# --------------------------------------------------

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
)

from config import INTERMEDIATE_DIR

# --------------------------------------------------
# PATHS (Portable)
# --------------------------------------------------

BASE_PATH = os.path.join(
    INTERMEDIATE_DIR,
    "instance1_base_raw.csv"
)

print("Loading base raw dataset...")
df = pd.read_csv(BASE_PATH)

father_col  = "20107-0.0"
mother_col  = "20110-0.0"
sibling_col = "20111-0.0"

# --------------------------------------------------
# Vectorized family history detection
# --------------------------------------------------

def contains_code_one(series):
    return (
        series
        .fillna("")
        .astype(str)
        .str.split(',')
        .apply(lambda x: any(code.strip().split('.')[0] == "1" for code in x))
    )

father_flag  = contains_code_one(df[father_col])
mother_flag  = contains_code_one(df[mother_col])
sibling_flag = contains_code_one(df[sibling_col])

df["fh_cvd"] = (
    father_flag |
    mother_flag |
    sibling_flag
).astype(int)

df_out = df[["eid","fh_cvd"]].copy()

# --------------------------------------------------
# SAVE (Portable)
# --------------------------------------------------

OUTPUT_PATH = os.path.join(
    INTERMEDIATE_DIR,
    "instance1_family_history.csv"
)

df_out.to_csv(OUTPUT_PATH, index=False)

print("Family history distribution:")
print(df_out["fh_cvd"].value_counts())
print(f"Saved to: {OUTPUT_PATH}")
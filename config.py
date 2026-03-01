import os

# Absolute path to project root (where config.py lives)
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(ROOT_DIR, "data")
INTERMEDIATE_DIR = os.path.join(DATA_DIR, "intermediate")
IMPUTED_DIR = os.path.join(DATA_DIR, "imputed")
RAW_DIR = os.path.join(DATA_DIR, "raw")

RESULTS_DIR = os.path.join(ROOT_DIR, "results")
LOGS_DIR = os.path.join(RESULTS_DIR, "logs")
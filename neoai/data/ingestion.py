from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]

RAW_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "Merged_industry_jobs_industry_jobs.csv"
)


def load_raw_data() -> pd.DataFrame:
    """Load the original merged industry-jobs dataset."""
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Raw dataset not found: {RAW_DATA_PATH}"
        )

    return pd.read_csv(RAW_DATA_PATH)
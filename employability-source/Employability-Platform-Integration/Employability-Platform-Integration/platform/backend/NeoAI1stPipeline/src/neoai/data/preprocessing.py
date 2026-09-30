import re

import numpy as np
import pandas as pd


def parse_salary(value):
    """Convert salary text or ranges into a numeric midpoint."""
    if pd.isna(value):
        return np.nan

    s = str(value).strip()

    if s.upper().replace(" ", "") == "NA":
        return np.nan

    if "," in s:
        return np.nan

    s = (
        s.replace("LPA", "")
        .replace("–", "-")
        .replace("—", "-")
        .strip()
    )

    numbers = [
        float(number)
        for number in re.findall(r"\d+\.?\d*", s)
    ]

    if not numbers:
        return np.nan

    return sum(numbers) / len(numbers)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the notebook's cleaning steps."""

    df = df.copy()

    df.columns = df.columns.str.strip()

    # Parse salary first.
    df["SalaryLPA_parsed"] = df["SalaryLPA"].apply(parse_salary)

    # Remove rows with missing or unparseable salary.
    df = df[df["SalaryLPA_parsed"].notna()].copy()

    # Impute the remaining missing values.
    df["Company"] = df["Company"].fillna("Unknown")
    df["Experience"] = df["Experience"].fillna("Unknown")

    # Remove duplicate records, excluding Job_ID.
    cols_no_id = [column for column in df.columns if column != "Job_ID"]

    df = df.drop_duplicates(
        subset=cols_no_id,
        keep="first",
    ).copy()

    return df.reset_index(drop=True)
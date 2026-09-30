import os
import pandas as pd


INPUT_FILE = "data/processed/Cleaned_Merged_Industry_Jobs.csv"
OUTPUT_FILE = "data/processed/Cleaned_Merged_Industry_Jobs_Zero_Outliers.csv"

SALARY_COLUMN = "SalaryLPA_parsed"


def remove_salary_outliers(
    input_file: str = INPUT_FILE,
    output_file: str = OUTPUT_FILE,
) -> pd.DataFrame:
    """
    Remove salary outlier rows using the IQR method.

    Outliers are defined as salary values outside:

        Lower Bound = Q1 - 1.5 * IQR
        Upper Bound = Q3 + 1.5 * IQR

    Outlier rows are completely removed from the dataset.
    Salary values are NOT replaced with zero.

    Methodology note — pre-CV IQR filtering
    ----------------------------------------
    IQR bounds are computed from the full dataset before cross-validation
    folds are created. This means the validation rows within each fold
    have already been filtered using statistics that include those same
    rows (target leakage in the strict sense).

    This is an accepted trade-off for a dataset-cleaning step:
    - The IQR filter removes extreme salary values that are likely data
      entry errors rather than genuine high-salary roles.
    - The alternative (per-fold IQR) would require integrating outlier
      removal into the sklearn Pipeline, significantly increasing
      pipeline complexity for marginal benefit on this dataset.
    - The impact is small because IQR bounds are stable statistics;
      removing a single fold's rows would shift Q1/Q3 by less than 1%.

    If strict per-fold filtering is required in future, wrap this logic
    in a sklearn TransformerMixin and add it as the first pipeline step.
    """

    if not os.path.exists(input_file):
        raise FileNotFoundError(
            f"Input dataset not found: {input_file}"
        )

    df = pd.read_csv(input_file)

    if SALARY_COLUMN not in df.columns:
        raise ValueError(
            f"Required salary column '{SALARY_COLUMN}' "
            f"not found in dataset."
        )

    # Convert salary column to numeric.
    # Invalid values become NaN.
    df[SALARY_COLUMN] = pd.to_numeric(
        df[SALARY_COLUMN],
        errors="coerce",
    )

    # Remove rows where salary is missing because
    # they cannot be evaluated for salary outliers.
    df = df.dropna(subset=[SALARY_COLUMN]).copy()

    # Calculate IQR
    q1 = df[SALARY_COLUMN].quantile(0.25)
    q3 = df[SALARY_COLUMN].quantile(0.75)

    iqr = q3 - q1

    # Calculate IQR bounds
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    print("\nSalary Outlier Detection")
    print("-" * 50)
    print(f"Q1:           {q1:.4f}")
    print(f"Q3:           {q3:.4f}")
    print(f"IQR:          {iqr:.4f}")
    print(f"Lower Bound:  {lower_bound:.4f}")
    print(f"Upper Bound:  {upper_bound:.4f}")

    original_rows = len(df)

    # Keep only rows inside the IQR boundaries.
    # Outlier rows are REMOVED completely.
    df = df[
        (df[SALARY_COLUMN] >= lower_bound)
        & (df[SALARY_COLUMN] <= upper_bound)
    ].copy()

    removed_rows = original_rows - len(df)

    # Create output directory if necessary.
    output_directory = os.path.dirname(output_file)

    if output_directory:
        os.makedirs(output_directory, exist_ok=True)

    # Save genuinely outlier-free dataset.
    df.to_csv(output_file, index=False)

    print("\nOutlier Removal Results")
    print("-" * 50)
    print(f"Rows before removal: {original_rows}")
    print(f"Rows removed:        {removed_rows}")
    print(f"Rows after removal:  {len(df)}")
    print(f"Output file:         {output_file}")

    return df


if __name__ == "__main__":
    remove_salary_outliers()
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]

EVALUATION_DIR = PROJECT_ROOT / "reports" / "evaluation"

ORIGINAL_RESULTS_PATH = (
    EVALUATION_DIR / "cross_validation_results.csv"
)

ZERO_OUTLIERS_RESULTS_PATH = (
    EVALUATION_DIR / "cross_validation_results_zero_outliers.csv"
)

OUTPUT_PATH = (
    EVALUATION_DIR / "combined_cross_validation_results.csv"
)


def load_results(file_path: Path, dataset_name: str) -> pd.DataFrame:
    """Load and validate a cross-validation results file."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Validation results not found:\n{file_path}"
        )

    df = pd.read_csv(file_path)

    if df.empty:
        raise ValueError(
            f"Validation results file is empty:\n{file_path}"
        )

    if "model" not in df.columns:
        raise ValueError(
            f"'model' column is missing from:\n{file_path}"
        )

    # Add dataset identifier.
    df["dataset"] = dataset_name

    return df


def add_dataset_rank(df: pd.DataFrame) -> pd.DataFrame:
    """Rank models within each dataset using mean R²."""

    if "mean_r2" not in df.columns:
        return df

    df["dataset_rank"] = (
        df.groupby("dataset")["mean_r2"]
        .rank(
            ascending=False,
            method="min",
        )
        .astype(int)
    )

    return df


def add_overall_rank(df: pd.DataFrame) -> pd.DataFrame:
    """Rank all dataset/model combinations using mean R²."""

    if "mean_r2" not in df.columns:
        return df

    df["overall_rank"] = (
        df["mean_r2"]
        .rank(
            ascending=False,
            method="min",
        )
        .astype(int)
    )

    return df


def main():
    print("Loading original dataset validation results...")

    original_df = load_results(
        ORIGINAL_RESULTS_PATH,
        "Original Dataset",
    )

    print("Loading zero-outlier validation results...")

    zero_outliers_df = load_results(
        ZERO_OUTLIERS_RESULTS_PATH,
        "Zero Outliers Dataset",
    )

    # ---------------------------------------------------------
    # Combine results
    # ---------------------------------------------------------

    combined_df = pd.concat(
        [
            original_df,
            zero_outliers_df,
        ],
        ignore_index=True,
    )

    # ---------------------------------------------------------
    # Columns to retain
    # ---------------------------------------------------------

    preferred_columns = [
        # Identification
        "dataset",
        "model",

        # Overall metrics
        "mean_mae",
        "std_mae",
        "mean_rmse",
        "std_rmse",
        "mean_r2",
        "std_r2",

        # Fold MAE
        "fold_1_mae",
        "fold_2_mae",
        "fold_3_mae",
        "fold_4_mae",
        "fold_5_mae",

        # Fold RMSE
        "fold_1_rmse",
        "fold_2_rmse",
        "fold_3_rmse",
        "fold_4_rmse",
        "fold_5_rmse",

        # Fold R²
        "fold_1_r2",
        "fold_2_r2",
        "fold_3_r2",
        "fold_4_r2",
        "fold_5_r2",
    ]

    available_columns = [
        column
        for column in preferred_columns
        if column in combined_df.columns
    ]

    combined_df = combined_df[available_columns]

    # ---------------------------------------------------------
    # Add rankings
    # ---------------------------------------------------------

    combined_df = add_dataset_rank(combined_df)

    combined_df = add_overall_rank(combined_df)

    # ---------------------------------------------------------
    # Sort results
    # ---------------------------------------------------------

    sort_columns = []

    if "overall_rank" in combined_df.columns:
        sort_columns.append("overall_rank")

    if "mean_r2" in combined_df.columns:
        sort_columns.append("mean_r2")

    if "mean_mae" in combined_df.columns:
        sort_columns.append("mean_mae")

    if "mean_rmse" in combined_df.columns:
        sort_columns.append("mean_rmse")

    if sort_columns:
        combined_df = combined_df.sort_values(
            by=sort_columns,
            ascending=[
                True if column == "overall_rank" else False
                for column in sort_columns
            ],
        )

    combined_df = combined_df.reset_index(drop=True)

    # ---------------------------------------------------------
    # Save combined results
    # ---------------------------------------------------------

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    combined_df.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    # ---------------------------------------------------------
    # Display results
    # ---------------------------------------------------------

    print("\n" + "=" * 80)
    print("COMBINED CROSS-VALIDATION RESULTS")
    print("=" * 80)

    print(
        combined_df.to_string(
            index=False
        )
    )

    print("\n" + "=" * 80)
    print("BEST MODEL PER DATASET")
    print("=" * 80)

    if "mean_r2" in combined_df.columns:

        best_models = (
            combined_df
            .sort_values(
                by="mean_r2",
                ascending=False,
            )
            .groupby(
                "dataset",
                as_index=False,
            )
            .first()
        )

        display_columns = [
            column
            for column in [
                "dataset",
                "model",
                "mean_mae",
                "mean_rmse",
                "mean_r2",
                "std_r2",
                "dataset_rank",
            ]
            if column in best_models.columns
        ]

        print(
            best_models[display_columns]
            .to_string(index=False)
        )

    print("\nSaved combined results to:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
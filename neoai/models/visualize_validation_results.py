from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[3]

INPUT_PATH = (
    PROJECT_ROOT
    / "reports"
    / "evaluation"
    / "combined_cross_validation_results.csv"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "reports"
    / "visualizations"
)


def load_results():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Validation report not found:\n{INPUT_PATH}"
        )

    return pd.read_csv(INPUT_PATH)


def plot_mean_r2(df):
    plt.figure(figsize=(10, 6))

    for dataset in df["dataset"].unique():
        dataset_df = df[df["dataset"] == dataset]

        plt.plot(
            dataset_df["model"],
            dataset_df["mean_r2"],
            marker="o",
            label=dataset,
        )

    plt.xlabel("Model")
    plt.ylabel("Mean R²")
    plt.title("Model Performance Comparison - Mean R²")
    plt.xticks(rotation=20)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    output = OUTPUT_DIR / "mean_r2_comparison.png"
    plt.savefig(output, dpi=300)
    plt.close()

    print(f"Saved: {output}")


def plot_fold_scores(df):
    fold_columns = [
        "fold_1_r2",
        "fold_2_r2",
        "fold_3_r2",
        "fold_4_r2",
        "fold_5_r2",
    ]

    available_folds = [
        column
        for column in fold_columns
        if column in df.columns
    ]

    if not available_folds:
        print("No fold-level R² columns found.")
        return

    rows = []

    for _, row in df.iterrows():
        for fold in available_folds:
            rows.append(
                {
                    "dataset": row["dataset"],
                    "model": row["model"],
                    "fold": fold,
                    "r2": row[fold],
                }
            )

    fold_df = pd.DataFrame(rows)

    plt.figure(figsize=(12, 7))

    labels = []
    values = []

    for _, row in fold_df.iterrows():
        labels.append(
            f"{row['dataset']} - {row['model']} - {row['fold']}"
        )
        values.append(row["r2"])

    plt.bar(
        range(len(values)),
        values,
    )

    plt.xlabel("Dataset / Model / Fold")
    plt.ylabel("R²")
    plt.title("Cross-Validation Fold R² Scores")
    plt.xticks(
        range(len(labels)),
        labels,
        rotation=90,
    )

    plt.tight_layout()

    output = OUTPUT_DIR / "fold_r2_comparison.png"
    plt.savefig(output, dpi=300)
    plt.close()

    print(f"Saved: {output}")


def plot_best_model(df):
    best_rows = (
        df.sort_values(
            "mean_r2",
            ascending=False,
        )
        .groupby("dataset")
        .first()
        .reset_index()
    )

    plt.figure(figsize=(8, 6))

    plt.bar(
        best_rows["dataset"],
        best_rows["mean_r2"],
    )

    plt.xlabel("Dataset")
    plt.ylabel("Best Mean R²")
    plt.title("Best Model Performance by Dataset")

    for index, row in best_rows.iterrows():
        plt.text(
            index,
            row["mean_r2"],
            f"{row['mean_r2']:.4f}\n{row['model']}",
            ha="center",
            va="bottom",
        )

    plt.tight_layout()

    output = OUTPUT_DIR / "best_model_comparison.png"
    plt.savefig(output, dpi=300)
    plt.close()

    print(f"Saved: {output}")


def main():
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("Loading validation results...")

    df = load_results()

    print("\nValidation results:")
    print(df.to_string(index=False))

    print("\nCreating visualizations...")

    plot_mean_r2(df)
    plot_fold_scores(df)
    plot_best_model(df)

    print("\nVisualization completed.")


if __name__ == "__main__":
    main()
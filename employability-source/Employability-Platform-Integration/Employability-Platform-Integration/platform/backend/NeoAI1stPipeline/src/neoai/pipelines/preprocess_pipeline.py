from pathlib import Path

from src.neoai.data.ingestion import load_raw_data
from src.neoai.data.preprocessing import clean_data
from src.neoai.features.build_features import build_features


PROJECT_ROOT = Path(__file__).resolve().parents[3]

PROCESSED_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "Cleaned_Merged_Industry_Jobs.csv"
)


def main():
    raw_df = load_raw_data()

    print("Raw shape:", raw_df.shape)

    clean_df = clean_data(raw_df)

    print("After cleaning:", clean_df.shape)

    feature_df = build_features(clean_df)

    print("Final shape:", feature_df.shape)

    PROCESSED_DATA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    feature_df.to_csv(PROCESSED_DATA_PATH, index=False)

    print(f"Saved to: {PROCESSED_DATA_PATH}")


if __name__ == "__main__":
    main()
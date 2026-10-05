from pathlib import Path
import shutil
import joblib


PROJECT_ROOT = Path(__file__).resolve().parents[3]


SOURCE_MODEL = (
    PROJECT_ROOT
    / "models"
    / "best_salary_model_zero_outliers_cv.pkl"
)


FINAL_MODEL = (
    PROJECT_ROOT
    / "models"
    / "final_salary_model.pkl"
)


def main():
    if not SOURCE_MODEL.exists():
        raise FileNotFoundError(
            f"Best CV model not found:\n{SOURCE_MODEL}"
        )

    FINAL_MODEL.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        SOURCE_MODEL,
        FINAL_MODEL,
    )

    print("Final salary model saved successfully.")
    print(f"Source : {SOURCE_MODEL}")
    print(f"Final  : {FINAL_MODEL}")

    # ========================================================
    # VERIFY FINAL MODEL
    # ========================================================

    model = joblib.load(FINAL_MODEL)

    print("\n" + "=" * 60)
    print("FINAL MODEL INFORMATION")
    print("=" * 60)

    # Model in use
    print("\nModel in use:")
    print(f"  {type(model).__name__}")

    # Pipeline steps
    if hasattr(model, "steps"):
        print("\nPipeline steps:")

        for name, step in model.steps:
            print(f"  - {name}: {type(step).__name__}")

        estimator = model.steps[-1][1]

    else:
        estimator = model

    # Hyperparameters
    print("\nHyperparameters:")

    if hasattr(estimator, "get_params"):
        params = estimator.get_params()

        for name, value in params.items():
            print(f"  {name}: {value}")
    else:
        print("  Hyperparameters could not be extracted.")

    # Features
    print("\nFeatures:")

    features = None

    if hasattr(model, "feature_names_in_"):
        features = model.feature_names_in_

    elif hasattr(estimator, "feature_names_in_"):
        features = estimator.feature_names_in_

    if features is not None:
        print(f"  Number of features: {len(features)}")

        for i, feature in enumerate(features, start=1):
            print(f"  {i}. {feature}")
    else:
        print("  Feature names are not directly available.")

    # Feature count
    print("\nFeature count:")

    if hasattr(model, "n_features_in_"):
        print(f"  {model.n_features_in_}")

    elif hasattr(estimator, "n_features_in_"):
        print(f"  {estimator.n_features_in_}")

    else:
        print("  Not available.")

    print("\n" + "=" * 60)
    print("MODEL VERIFICATION COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
# =============================================================================
# BASELINE TRAINING — train_salary_zero_outliers.py
# =============================================================================
# Purpose : Quick baseline comparison using a simple train/test split
#           on the IQR-filtered (zero-outlier) dataset.
#           Raw numeric features only — no CompanyFrequencyEncoder,
#           no SkillScaler, no add_static_features pipeline.
#           Output : models/best_salary_model_zero_outliers.pkl
#
# Final model path (different) :
#   cross_val_score_zero_outliers.py
#   → 5-fold CV with the full 18-feature sklearn Pipeline
#   → models/best_salary_model_zero_outliers_cv.pkl
#   → models/final_salary_model.pkl
# =============================================================================
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.svm import SVR
import yaml
from xgboost import XGBRegressor


PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "Cleaned_Merged_Industry_Jobs_Zero_Outliers.csv"
)

MODEL_DIR = PROJECT_ROOT / "models"
REPORT_DIR = PROJECT_ROOT / "reports" / "evaluation"

BEST_MODEL_PATH = MODEL_DIR / "best_salary_model_zero_outliers.pkl"
RESULTS_PATH = REPORT_DIR / "model_comparison_zero_outliers.csv"
PARAMS_PATH = PROJECT_ROOT / "params.yaml"


# ============================================================
# LOAD PARAMETERS
# ============================================================

with open(PARAMS_PATH, "r") as f:
    params = yaml.safe_load(f)

def load_dataset():
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    return pd.read_csv(DATA_PATH)


def prepare_features(df):
    target_column = "SalaryLPA_parsed"

    columns_to_remove = [
            "SalaryLPA",
            "SalaryLPA_parsed",
            "SalaryLPA_capped",
            "SalaryLPA_capped_scaled",
            "Company",
            "Role",
            "Role_Group",
            "Experience",
            "Experience_Level",
            "Link of the Job",
            "Link of the Job ",
            "Job_ID",
            'PythonRequired', 
            'LinuxRequired', 
            'NetworkingRequired', 
            'AWSRequired', 
            'AzureRequired',
            'DockerRequired', 
            'KubernetesRequired', 
            'TerraformRequired', 
            'CyberSecurityRequired', 
            'CommunicationRequired',
            'Experience_Unknown',
        ]   

    X = df.drop(columns=columns_to_remove, errors="ignore")
    y = df[target_column]

    # Use only numeric columns.
    X = X.select_dtypes(include=["number"])

    # Remove rows containing missing values.
    valid_rows = X.notna().all(axis=1) & y.notna()

    X = X.loc[valid_rows]
    y = y.loc[valid_rows]

    return X, y


def create_models():
    rf_params = params["models"]["random_forest"]
    xgb_params = params["models"]["xgboost"]

    return {
        "LinearRegression": LinearRegression(),

        "RandomForest": RandomForestRegressor(
            n_estimators=rf_params["n_estimators"],
            max_depth=rf_params["max_depth"],
            random_state=rf_params["random_state"],
            n_jobs=rf_params["n_jobs"],
        ),

        "SVR": SVR(
            kernel="rbf",
            C=100,
            epsilon=0.1,
        ),

        "XGBRegressor": XGBRegressor(
                n_estimators=xgb_params["n_estimators"],
                max_depth=xgb_params["max_depth"],
                learning_rate=xgb_params["learning_rate"],
                subsample=xgb_params["subsample"],
                colsample_bytree=xgb_params["colsample_bytree"],
                objective=xgb_params["objective"],
                random_state=xgb_params["random_state"],
                n_jobs=xgb_params["n_jobs"],
            ),
    }


def evaluate_model(model, X_train, X_test, y_train, y_test):
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)

    mae = mean_absolute_error(y_test, predictions)
    mse = mean_squared_error(y_test, predictions)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, predictions)

    return model, {
        "mae": float(mae),
        "mse": float(mse),
        "rmse": float(rmse),
        "r2": float(r2),
    }


def main():
    df = load_dataset()

    print("Loaded dataset:", df.shape)

    X, y = prepare_features(df)

    print("Feature shape:", X.shape)
    print("Target shape:", y.shape)
    print("Columns:", X.columns.tolist())

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
    )

    models = create_models()

    results = []
    trained_models = {}

    mlflow.set_experiment("NeoAI Salary Prediction - Zero Outliers")

    for model_name, model in models.items():
        print(f"\nTraining {model_name}...")

        with mlflow.start_run(run_name=model_name):
            trained_model, metrics = evaluate_model(
                model,
                X_train,
                X_test,
                y_train,
                y_test,
            )

            trained_models[model_name] = trained_model

            mlflow.log_param("model_name", model_name)
            mlflow.log_param("training_rows", len(X_train))
            mlflow.log_param("testing_rows", len(X_test))
            mlflow.log_param("feature_count", X.shape[1])
            mlflow.log_param("random_state", 42)

            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)

            mlflow.sklearn.log_model(
                trained_model,
                artifact_path="model",
                skops_trusted_types=[
                    "sklearn.tree._tree.Tree",
                    "xgboost.core.Booster",
                    "xgboost.sklearn.XGBRegressor",
                ],
            )

            result = {
                "model": model_name,
                **metrics,
            }

            results.append(result)

            print(f"MAE:  {metrics['mae']:.4f}")
            print(f"RMSE: {metrics['rmse']:.4f}")
            print(f"R2:   {metrics['r2']:.4f}")

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(
        by="r2",
        ascending=False,
    ).reset_index(drop=True)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    results_df.to_csv(RESULTS_PATH, index=False)

    best_model_name = results_df.iloc[0]["model"]
    best_model = trained_models[best_model_name]

    joblib.dump(best_model, BEST_MODEL_PATH)

    print("\nModel comparison:")
    print(results_df.to_string(index=False))

    print(f"\nBest model: {best_model_name}")
    print(f"Best model saved to: {BEST_MODEL_PATH}")
    print(f"Comparison saved to: {RESULTS_PATH}")


if __name__ == "__main__":
    main()
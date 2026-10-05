from pathlib import Path
import os
import joblib
import numpy as np
import pandas as pd
import yaml

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import KFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from xgboost import XGBRegressor
from src.neoai.features.build_features import (
    add_static_features,
    normalize_experience,
    EXPERIENCE_ENCODING,
    group_role,
)
from src.neoai.models.transformers import (
    CompanyFrequencyEncoder,
    SkillScaler,
    FinalFeatureSelector,
)

# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "Cleaned_Merged_Industry_Jobs_Zero_Outliers.csv"
)

OUTPUT_MODEL = (
    PROJECT_ROOT
    / "models"
    / "best_salary_model_zero_outliers_cv.pkl"
)

OUTPUT_REPORT = (
    PROJECT_ROOT
    / "reports"
    / "evaluation"
    / "cross_validation_results_zero_outliers.csv"
)

PARAMS_PATH = PROJECT_ROOT / "params.yaml"


# ============================================================
# LOAD PARAMETERS
# ============================================================

with open(PARAMS_PATH, "r") as f:
    params = yaml.safe_load(f)


# ============================================================
# CONSTANTS
# ============================================================

TARGET_COLUMN = "SalaryLPA_parsed"

SKILL_COLS = [
    "PythonRequired",
    "LinuxRequired",
    "NetworkingRequired",
    "AWSRequired",
    "AzureRequired",
    "DockerRequired",
    "KubernetesRequired",
    "TerraformRequired",
    "CyberSecurityRequired",
    "CommunicationRequired",
]




# ============================================================
# MODELS
# ============================================================

def get_models():

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
            gamma="scale",
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


# ============================================================
# CREATE FOLD-SAFE PIPELINE
# ============================================================

def create_pipeline(model):

    FINAL_FEATURES = [
    "Role_Group_Cloud Engineer",
    "Role_Group_DevOps Engineer",
    "Role_Group_Network Engineer",
    "Role_Group_Other",
    "Role_Group_Security/SOC Analyst",
    "Role_Group_Site Reliability Engineer",
    "Experience_Encoded",
    "Company_Freq",
    "PythonRequired_scaled",
    "LinuxRequired_scaled",
    "NetworkingRequired_scaled",
    "AWSRequired_scaled",
    "AzureRequired_scaled",
    "DockerRequired_scaled",
    "KubernetesRequired_scaled",
    "TerraformRequired_scaled",
    "CyberSecurityRequired_scaled",
    "CommunicationRequired_scaled",
    ]

    return Pipeline(
        steps=[

            # ------------------------------------------------
            # 1. Company frequency
            # ------------------------------------------------

            (
                "company_frequency",
                CompanyFrequencyEncoder(
                    column="Company"
                ),
            ),

            # ------------------------------------------------
            # 2. Skill scaling
            # ------------------------------------------------

            (
                "skill_scaler",
                SkillScaler(
                    columns=SKILL_COLS
                ),
            ),

            # ------------------------------------------------
            # 3. Final feature selection
            # ------------------------------------------------

            (
                "feature_selector",
                FinalFeatureSelector(feature_columns=FINAL_FEATURES),
            ),

            # ------------------------------------------------
            # 4. Model
            # ------------------------------------------------

            (
                "model",
                model,
            ),
        ]
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("ZERO-OUTLIER FOLD-SAFE CROSS VALIDATION")
    print("=" * 70)

    # ========================================================
    # LOAD DATA
    # ========================================================

    print("\nLoading dataset...")

    df = pd.read_csv(DATA_PATH)

    print(
        f"Dataset shape: {df.shape}"
    )

    if TARGET_COLUMN not in df.columns:
        raise ValueError(
            f"Target column '{TARGET_COLUMN}' "
            f"not found in dataset."
        )

    # ========================================================
    # STATIC FEATURES
    # ========================================================

    print(
        "\nApplying static feature engineering..."
    )

    df = add_static_features(df)

    # ========================================================
    # X / y
    # ========================================================

    X = df.drop(
        columns=[TARGET_COLUMN]
    )

    y = pd.to_numeric(
        df[TARGET_COLUMN],
        errors="coerce",
    )

    valid_target_mask = y.notna()

    X = (
        X.loc[valid_target_mask]
        .reset_index(drop=True)
    )

    y = (
        y.loc[valid_target_mask]
        .reset_index(drop=True)
    )

    print(
        f"Features before CV: {X.shape}"
    )

    print(
        f"Target shape: {y.shape}"
    )

    # ========================================================
    # CROSS VALIDATION
    # ========================================================

    cv_params = params["cross_validation"]

    kfold = KFold(
        n_splits=cv_params["n_splits"],
        shuffle=cv_params["shuffle"],
        random_state=cv_params["random_state"],
    )

    # ========================================================
    # MODELS
    # ========================================================

    models = get_models()

    # ========================================================
    # METRICS
    # ========================================================

    scoring = {
        "mae": "neg_mean_absolute_error",
        "rmse": "neg_root_mean_squared_error",
        "r2": "r2",
    }

    results = []

    # ========================================================
    # MODEL EVALUATION
    # ========================================================

    for model_name, model in models.items():

        print("\n" + "-" * 70)
        print(
            f"Evaluating {model_name}"
        )
        print("-" * 70)

        pipeline = create_pipeline(
            model
        )

        scores = cross_validate(
            pipeline,
            X,
            y,
            cv=kfold,
            scoring=scoring,
            n_jobs=-1,
            return_train_score=False,
        )

        # ----------------------------------------------------
        # Convert negative scoring values
        # ----------------------------------------------------

        mae_values = (
            -scores["test_mae"]
        )

        rmse_values = (
            -scores["test_rmse"]
        )

        r2_values = (
            scores["test_r2"]
        )

        # ----------------------------------------------------
        # Print fold metrics
        # ----------------------------------------------------

        print(
            "\nFold MAE:"
        )

        print(
            np.round(
                mae_values,
                6,
            )
        )

        print(
            "\nFold RMSE:"
        )

        print(
            np.round(
                rmse_values,
                6,
            )
        )

        print(
            "\nFold R²:"
        )

        print(
            np.round(
                r2_values,
                6,
            )
        )

        # ----------------------------------------------------
        # Print mean metrics
        # ----------------------------------------------------

        print(
            f"\nMean MAE : "
            f"{mae_values.mean():.6f}"
        )

        print(
            f"Mean RMSE: "
            f"{rmse_values.mean():.6f}"
        )

        print(
            f"Mean R²  : "
            f"{r2_values.mean():.6f}"
        )

        print(
            f"Std MAE  : "
            f"{mae_values.std():.6f}"
        )

        print(
            f"Std RMSE : "
            f"{rmse_values.std():.6f}"
        )

        print(
            f"Std R²   : "
            f"{r2_values.std():.6f}"
        )

        # ----------------------------------------------------
        # Store results
        # ----------------------------------------------------

        results.append(
            {
                "model": model_name,

                "mean_mae":
                    mae_values.mean(),

                "std_mae":
                    mae_values.std(),

                "mean_rmse":
                    rmse_values.mean(),

                "std_rmse":
                    rmse_values.std(),

                "mean_r2":
                    r2_values.mean(),

                "std_r2":
                    r2_values.std(),

                # MAE folds
                "fold_1_mae":
                    mae_values[0],

                "fold_2_mae":
                    mae_values[1],

                "fold_3_mae":
                    mae_values[2],

                "fold_4_mae":
                    mae_values[3],

                "fold_5_mae":
                    mae_values[4],

                # RMSE folds
                "fold_1_rmse":
                    rmse_values[0],

                "fold_2_rmse":
                    rmse_values[1],

                "fold_3_rmse":
                    rmse_values[2],

                "fold_4_rmse":
                    rmse_values[3],

                "fold_5_rmse":
                    rmse_values[4],

                # R² folds
                "fold_1_r2":
                    r2_values[0],

                "fold_2_r2":
                    r2_values[1],

                "fold_3_r2":
                    r2_values[2],

                "fold_4_r2":
                    r2_values[3],

                "fold_5_r2":
                    r2_values[4],
            }
        )

    # ========================================================
    # RESULTS DATAFRAME
    # ========================================================

    results_df = pd.DataFrame(
        results
    )

    # Higher R² = better
    results_df = (
        results_df
        .sort_values(
            by="mean_r2",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    print(
        "\nresults_df"
    )

    print(
        results_df.to_string(
            index=False
        )
    )

    # ========================================================
    # SELECT MODEL
    # ========================================================

    selected_model_name = (
        results_df.iloc[0]["model"]
    )

    print(
        "\nSelected model:"
    )

    print(
        selected_model_name
    )

    # ========================================================
    # TRAIN SELECTED MODEL ON COMPLETE
    # ZERO-OUTLIER DATASET
    # ========================================================

    selected_model = create_pipeline(
        models[selected_model_name]
    )

    print(
        "\nTraining selected model "
        "on complete zero-outlier dataset..."
    )

    selected_model.fit(
        X,
        y,
    )

    # ========================================================
    # SAVE MODEL
    # ========================================================

    os.makedirs(
        OUTPUT_MODEL.parent,
        exist_ok=True,
    )

    os.makedirs(
        OUTPUT_REPORT.parent,
        exist_ok=True,
    )

    joblib.dump(
        selected_model,
        OUTPUT_MODEL,
    )

    results_df.to_csv(
        OUTPUT_REPORT,
        index=False,
    )

    # ========================================================
    # FINAL REPORT
    # ========================================================

    selected = results_df.iloc[0]

    print(
        "\n" + "=" * 70
    )

    print(
        "FINAL CROSS-VALIDATION COMPARISON"
    )

    print(
        "=" * 70
    )

    print(
        results_df[
            [
                "model",
                "mean_mae",
                "std_mae",
                "mean_rmse",
                "std_rmse",
                "mean_r2",
                "std_r2",
            ]
        ].to_string(
            index=False
        )
    )

    # ========================================================
    # SELECTED MODEL METRICS
    # ========================================================

    print(
        "\n" + "=" * 70
    )

    print(
        "SELECTED MODEL"
    )

    print(
        "=" * 70
    )

    print(
        f"Model : "
        f"{selected_model_name}"
    )

    print(
        f"MAE   : "
        f"{selected['mean_mae']:.4f} LPA"
    )

    print(
        f"RMSE  : "
        f"{selected['mean_rmse']:.4f} LPA"
    )

    print(
        f"R²    : "
        f"{selected['mean_r2']:.4f}"
    )

    # ========================================================
    # OUTPUT PATHS
    # ========================================================

    print(
        "\nModel saved to:"
    )

    print(
        OUTPUT_MODEL
    )

    print(
        "\nEvaluation report:"
    )

    print(
        OUTPUT_REPORT
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "ZERO-OUTLIER FOLD-SAFE "
        "CROSS-VALIDATION COMPLETE"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":
    main()  
from pathlib import Path

import joblib
import pandas as pd

from src.neoai.features.build_features import add_static_features

PROJECT_ROOT = Path(__file__).resolve().parents[3]

MODEL_PATH = PROJECT_ROOT / "models" / "final_salary_model.pkl"

# ---------------------------------------------------------------------------
# Required raw input columns.
# Skill columns must be integers on a 1–10 scale, matching the training data.
# Experience and Role are raw strings; add_static_features() normalises them.
# ---------------------------------------------------------------------------
REQUIRED_INPUT_COLUMNS = [
    "Company",
    "Role",
    "Experience",
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


def predict_salary(input_data: dict | pd.DataFrame) -> float:
    """
    Predict salary in LPA for a single job profile.

    Parameters
    ----------
    input_data : dict or single-row DataFrame
        Must contain all keys in REQUIRED_INPUT_COLUMNS.
        Skill columns (PythonRequired … CommunicationRequired) must be
        integers on a 1–10 scale (1 = low requirement, 10 = high requirement).
        Experience is a raw string; accepted values include:
            "Fresher", "fresher", "0-1", "0-1 years", "0-2", "0-2 Years",
            "0-3", "Fresher  1 Year", "Fresher2 Years", etc.

    Returns
    -------
    float
        Predicted salary in LPA.
    """
    model = joblib.load(MODEL_PATH)

    if isinstance(input_data, dict):
        df = pd.DataFrame([input_data])
    else:
        df = input_data.copy().reset_index(drop=True)

    df = add_static_features(df)

    prediction = model.predict(df)
    return float(prediction[0])


def main():
    # Skill values use the 1–10 scale that matches the training data.
    # (Training dataset range: min=1, max=10, mean ~5–8 per skill.)
    sample = {
        "Company": "Infosys",
        "Role": "DevOps Engineer",
        "Experience": "Fresher",
        "PythonRequired": 7,
        "LinuxRequired": 8,
        "NetworkingRequired": 5,
        "AWSRequired": 7,
        "AzureRequired": 4,
        "DockerRequired": 7,
        "KubernetesRequired": 6,
        "TerraformRequired": 5,
        "CyberSecurityRequired": 3,
        "CommunicationRequired": 8,
    }

    print("Input:")
    for k, v in sample.items():
        print(f"  {k}: {v}")

    salary = predict_salary(sample)

    print(f"\nPredicted salary: {salary:.2f} LPA")


if __name__ == "__main__":
    main()

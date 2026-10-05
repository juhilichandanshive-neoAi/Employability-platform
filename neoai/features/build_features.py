import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer


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

# Skill columns accept integer values on a 1–10 scale,
# matching the training dataset range (min=1, max=10).
# Do NOT pass 0/1 binary flags — use the actual numeric
# importance/requirement level from the job posting.
SKILL_INPUT_SCALE = "1–10 integer (1 = low requirement, 10 = high requirement)"

# ============================================================
# EXPERIENCE NORMALISATION
# Canonical function used by preprocessing, CV, and prediction.
# Covers every value present in the actual dataset.
# ============================================================

def normalize_experience(value) -> str:
    """
    Normalise a raw Experience string to one of six canonical labels.

    Canonical labels and their ordinal encoding (see EXPERIENCE_ENCODING):
        Fresher/Entry Level  → 0
        0-1 Years            → 1
        0-2 Years            → 2
        0-3 Years            → 3
        Fresher-Mixed        → 3   (fresher + explicit year range)
        Unknown              → -1

    This function is the single source of truth used by:
        - src/neoai/pipelines/preprocess_pipeline.py  (via build_features)
        - src/neoai/models/cross_val_score.py
        - src/neoai/models/cross_val_score_zero_outliers.py
        - src/neoai/models/predict_salary.py
    """
    if pd.isna(value):
        return "Unknown"

    s = str(value).strip().lower()

    # Normalise dash variants
    s_clean = s.replace("\u2013", "-").replace("\u2014", "-")

    if "unknown" in s_clean:
        return "Unknown"

    # Fresher with an explicit year range attached
    # e.g. "Fresher  1 Year", "Fresher2 Years", "Fresher  3 Years"
    if "fresher" in s_clean and any(
        ch in s_clean for ch in ["1", "2", "3"]
    ):
        return "Fresher-Mixed"

    # Plain fresher / entry level / internship
    if "fresher" in s_clean or "entry" in s_clean or "internship" in s_clean:
        return "Fresher/Entry Level"

    if "0-1" in s_clean or "01" in s_clean:
        return "0-1 Years"

    if "0-2" in s_clean or "02" in s_clean:
        return "0-2 Years"

    if "0-3" in s_clean or "03" in s_clean:
        return "0-3 Years"

    return "Unknown"


EXPERIENCE_ENCODING = {
    "Fresher/Entry Level": 0,
    "0-1 Years":           1,
    "0-2 Years":           2,
    "0-3 Years":           3,
    "Fresher-Mixed":       3,
    "Unknown":            -1,
}


def group_role(role: str) -> str:
    role = str(role).lower()

    if "devops" in role:
        return "DevOps Engineer"

    if "site reliability" in role or "sre" in role:
        return "Site Reliability Engineer"

    if (
        "cyber" in role
        or "security analyst" in role
        or "soc" in role
        or "security engineer" in role
    ):
        return "Security/SOC Analyst"

    if "cloud" in role:
        return "Cloud Engineer"

    if "network" in role:
        return "Network Engineer"

    return "Other"


def add_static_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all deterministic (non-learned) features required by the pipeline.

    Safe to call on data that already contains role dummy columns.
    Uses the canonical normalize_experience / EXPERIENCE_ENCODING defined
    in this module — the single source of truth for all pipeline stages.
    """
    df = df.copy()

    # ------------------------------------------------------------------
    # Role grouping + one-hot encoding
    # ------------------------------------------------------------------
    if "Role_Group" not in df.columns:
        df["Role_Group"] = df["Role"].apply(group_role)

    role_dummy_columns = [
        "Role_Group_Cloud Engineer",
        "Role_Group_DevOps Engineer",
        "Role_Group_Network Engineer",
        "Role_Group_Other",
        "Role_Group_Security/SOC Analyst",
        "Role_Group_Site Reliability Engineer",
    ]

    missing_role_columns = [
        col for col in role_dummy_columns if col not in df.columns
    ]

    if missing_role_columns:
        role_dummies = pd.get_dummies(
            df["Role_Group"], prefix="Role_Group", dtype=int
        )
        for col in missing_role_columns:
            df[col] = role_dummies[col] if col in role_dummies.columns else 0

    # ------------------------------------------------------------------
    # Experience normalisation + ordinal encoding
    # ------------------------------------------------------------------
    if "Experience_Level" not in df.columns:
        df["Experience_Level"] = df["Experience"].apply(normalize_experience)

    if "Experience_Encoded" not in df.columns:
        df["Experience_Encoded"] = (
            df["Experience_Level"]
            .map(EXPERIENCE_ENCODING)
            .fillna(-1)
            .astype(float)
        )

    if "Experience_Unknown" not in df.columns:
        df["Experience_Unknown"] = (
            df["Experience_Encoded"] == -1
        ).astype(int)

    return df


# ============================================================
# SKLEARN TRANSFORMERS
# ============================================================

class CompanyFrequencyEncoder(BaseEstimator, TransformerMixin):
    """Fold-safe company frequency encoder."""

    def __init__(self, column="Company"):
        self.column = column

    def fit(self, X, y=None):
        X = pd.DataFrame(X).copy()
        self.frequency_map_ = (
            X[self.column].value_counts(normalize=True).to_dict()
        )
        return self

    def transform(self, X):
        X = pd.DataFrame(X).copy()
        X["Company_Freq"] = (
            X[self.column].map(self.frequency_map_).fillna(0.0)
        )
        return X


class SkillScaler(BaseEstimator, TransformerMixin):
    """
    Fold-safe StandardScaler for skill columns.

    Expects skill values on a 1–10 integer scale matching the
    training dataset. Values outside this range will produce
    z-scores beyond the training distribution.
    """

    def __init__(self, columns):
        self.columns = columns

    def fit(self, X, y=None):
        X = X.copy()
        self.imputer_ = SimpleImputer(strategy="median")
        imputed = self.imputer_.fit_transform(X[self.columns])
        self.scaler_ = StandardScaler()
        self.scaler_.fit(imputed)
        return self

    def transform(self, X):
        X = X.copy()
        imputed = self.imputer_.transform(X[self.columns])
        scaled = self.scaler_.transform(imputed)
        scaled_cols = [f"{c}_scaled" for c in self.columns]
        scaled_df = pd.DataFrame(scaled, columns=scaled_cols, index=X.index)
        X = X.drop(columns=scaled_cols, errors="ignore")
        return pd.concat([X, scaled_df], axis=1)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Entry point used by preprocess_pipeline.py.
    Only applies deterministic/static features.
    Learned transformations (CompanyFrequencyEncoder, SkillScaler)
    must be fitted inside CV folds, not here.
    """
    return add_static_features(df)

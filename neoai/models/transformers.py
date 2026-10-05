import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler


class CompanyFrequencyEncoder(BaseEstimator, TransformerMixin):
    """
    Fold-safe company frequency encoder.
    """

    def __init__(self, column="Company"):
        self.column = column

    def fit(self, X, y=None):
        X = X.copy()

        frequencies = (
            X[self.column]
            .value_counts(normalize=True)
        )

        self.frequency_map_ = frequencies.to_dict()

        return self

    def transform(self, X):
        X = X.copy()

        X["Company_Freq"] = (
            X[self.column]
            .map(self.frequency_map_)
            .fillna(0.0)
        )

        return X


class SkillScaler(BaseEstimator, TransformerMixin):
    """
    Fold-safe StandardScaler for skill columns.
    """

    def __init__(self, columns):
        self.columns = columns

    def fit(self, X, y=None):
        X = X.copy()

        self.scaler_ = StandardScaler()

        self.scaler_.fit(X[self.columns])

        return self

    def transform(self, X):
        X = X.copy()

        scaled_values = self.scaler_.transform(
            X[self.columns]
        )

        scaled_columns = [
            f"{column}_scaled"
            for column in self.columns
        ]

        scaled_df = pd.DataFrame(
            scaled_values,
            columns=scaled_columns,
            index=X.index,
        )

        X = X.drop(
            columns=scaled_columns,
            errors="ignore",
        )

        X = pd.concat(
            [X, scaled_df],
            axis=1,
        )

        return X
    

class FinalFeatureSelector(BaseEstimator, TransformerMixin):
    """
    Select the final features used by the salary prediction models.
    """

    def __init__(self, feature_columns):
        self.feature_columns = feature_columns

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()

        missing_columns = [
            column
            for column in self.feature_columns
            if column not in X.columns
        ]

        if missing_columns:
            raise ValueError(
                f"Missing required features: {missing_columns}"
            )

        return X[self.feature_columns].copy()
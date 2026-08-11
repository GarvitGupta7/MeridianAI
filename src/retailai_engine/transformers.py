"""Reusable scikit-learn compatible transformers for Meridian pipelines."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


class RequiredColumnsTransformer(BaseEstimator, TransformerMixin):
    """Validate and retain the columns required by a downstream pipeline."""

    def __init__(self, columns: Sequence[str]):
        self.columns = tuple(columns)

    def fit(self, X: pd.DataFrame, y: pd.Series | None = None):
        self._validate_columns(X)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        self._validate_columns(X)
        return X.loc[:, list(self.columns)].copy()

    def _validate_columns(self, dataframe: pd.DataFrame) -> None:
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("Pipeline input must be a pandas DataFrame.")
        missing = [column for column in self.columns if column not in dataframe]
        if missing:
            raise ValueError(f"Missing required column(s): {', '.join(missing)}.")


class NumericCoercionTransformer(BaseEstimator, TransformerMixin):
    """Convert selected dataframe columns to numeric values without silent loss."""

    def __init__(self, columns: Sequence[str]):
        self.columns = tuple(columns)

    def fit(self, X: pd.DataFrame, y: pd.Series | None = None):
        RequiredColumnsTransformer(self.columns).fit(X)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        transformed = X.copy()
        RequiredColumnsTransformer(self.columns).fit(transformed)
        for column in self.columns:
            transformed[column] = pd.to_numeric(transformed[column], errors="raise")
        return transformed

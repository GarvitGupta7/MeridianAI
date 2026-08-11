"""Reusable production preprocessing pipelines for RetailAI capabilities.

This module is additive: Meridian's existing workflow is untouched.  These
transformers provide a single reusable preprocessing contract for new ML APIs
and batch jobs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


DEFAULT_FEATURES = [
    "recency_days",
    "frequency",
    "monetary_value",
    "avg_order_value",
    "tenure_days",
    "purchase_rate",
    "return_rate",
    "product_diversity",
]


class RetailFeatureSelector(BaseEstimator, TransformerMixin):
    """Select and numerically sanitise the shared customer feature contract."""

    def __init__(self, features: Iterable[str] = DEFAULT_FEATURES):
        self.features = tuple(features)

    def fit(self, X, y=None):
        frame = pd.DataFrame(X)
        missing = [c for c in self.features if c not in frame.columns]
        if missing:
            raise ValueError(f"Missing required features: {', '.join(missing)}")
        return self

    def transform(self, X):
        frame = pd.DataFrame(X)
        missing = [c for c in self.features if c not in frame.columns]
        if missing:
            raise ValueError(f"Missing required features: {', '.join(missing)}")
        return frame.loc[:, self.features].replace([np.inf, -np.inf], np.nan).fillna(0.0).astype(float)


def build_scaled_customer_pipeline(features: Iterable[str] = DEFAULT_FEATURES) -> Pipeline:
    """Return the standard selector + scaler used by additive ML modules."""
    return Pipeline([
        ("features", RetailFeatureSelector(features)),
        ("scaler", StandardScaler()),
    ])


@dataclass(frozen=True)
class PreprocessingContract:
    features: tuple[str, ...] = tuple(DEFAULT_FEATURES)

    def validate(self, frame: pd.DataFrame) -> None:
        missing = [c for c in self.features if c not in frame.columns]
        if missing:
            raise ValueError(f"Missing required customer features: {', '.join(missing)}")

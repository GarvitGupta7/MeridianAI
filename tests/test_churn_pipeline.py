"""
==========================================================
Meridian

Module:
Churn Pipeline Tests

Description:
Tests reusable churn feature engineering and verifies
that the churn pipeline supports API-style predictions.

Author:
Garvit Gupta

Version:
2.0.0

Last Updated:
July 2026
==========================================================
"""

import pandas as pd

from src.preprocessing.feature_engineering import (
    CHURN_FEATURES,
    CustomerFeatureTransformer,
)
from src.training.train_churn import build_churn_pipeline


def sample_customer_data() -> pd.DataFrame:
    """Return a small, valid churn feature dataset for tests."""
    return pd.DataFrame(
        {
            "Recency": [2, 15, 30, 90],
            "Frequency": [12, 8, 4, 1],
            "Monetary": [1200.0, 750.0, 300.0, 50.0],
            "CustomerScore": [0.9, 0.7, 0.4, 0.1],
        }
    )


def test_feature_transformer_keeps_expected_columns():
    """The transformer must retain the agreed feature order."""
    transformed_data = CustomerFeatureTransformer().fit_transform(
        sample_customer_data()
    )

    assert list(transformed_data.columns) == CHURN_FEATURES


def test_churn_pipeline_predicts_for_one_customer():
    """The saved pipeline design must support API-style single predictions."""
    training_data = sample_customer_data()
    target = [0, 0, 1, 1]
    pipeline = build_churn_pipeline()
    pipeline.fit(training_data, target)

    prediction = pipeline.predict(training_data.iloc[[0]])

    assert prediction.shape == (1,)

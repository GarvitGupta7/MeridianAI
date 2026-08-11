"""
==========================================================
Meridian

Module:
Forecast Pipeline Tests

Description:
Tests leakage-free feature creation and verifies the
forecast pipeline supports a next-month style prediction.

Author:
Garvit Gupta

Version:
2.0.0

Last Updated:
July 2026
==========================================================
"""

import pandas as pd

from src.forecasting.feature_engineering import (
    FORECAST_FEATURES,
    create_forecast_features,
    create_next_month_features,
)
from src.forecasting.train_forecast import build_forecast_pipeline


def monthly_sales_history() -> pd.DataFrame:
    """Return enough monthly history to build lag and rolling features."""
    return pd.DataFrame(
        {
            "InvoiceDate": pd.date_range("2024-01-31", periods=24, freq="ME"),
            "Sales": [1000 + month * 25 for month in range(24)],
        }
    )


def test_forecast_features_only_use_historical_values():
    """The first feature row should use prior, not current, sales values."""
    features = create_forecast_features(monthly_sales_history())

    assert features.iloc[0]["Lag_1"] == 1275
    assert list(features[FORECAST_FEATURES].columns) == FORECAST_FEATURES


def test_forecast_pipeline_predicts_next_month():
    """The pipeline must accept the next-month feature record."""
    history = monthly_sales_history()
    training_data = create_forecast_features(history)
    pipeline = build_forecast_pipeline()
    pipeline.fit(training_data[FORECAST_FEATURES], training_data["Sales"])
    _, next_features = create_next_month_features(history)

    prediction = pipeline.predict(next_features)

    assert prediction.shape == (1,)

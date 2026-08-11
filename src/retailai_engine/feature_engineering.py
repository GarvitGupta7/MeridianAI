"""
==========================================================
Meridian

Module:
Forecast Feature Engineering

Description:
Builds leakage-free monthly sales features for production
forecasting using only information available before the
month being predicted.

Author:
Garvit Gupta

Version:
2.0.0

Last Updated:
July 2026
==========================================================
"""

from __future__ import annotations

import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin


FORECAST_FEATURES = [
    "Year",
    "Month",
    "Quarter",
    "Lag_1",
    "Lag_2",
    "Lag_3",
    "Lag_6",
    "RollingMean_3",
    "RollingMean_6",
    "RollingMean_12",
]


class ForecastFeatureTransformer(BaseEstimator, TransformerMixin):
    """Validate and retain the feature order used by the forecasting model."""

    def fit(self, X: pd.DataFrame, y: pd.Series | None = None):
        """Validate model-training features."""
        self._validate_input(X)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Return numeric forecasting features in their required order."""
        self._validate_input(X)
        transformed_data = X.loc[:, FORECAST_FEATURES].copy()

        for feature_name in FORECAST_FEATURES:
            transformed_data[feature_name] = pd.to_numeric(
                transformed_data[feature_name],
                errors="raise",
            )

        return transformed_data

    @staticmethod
    def _validate_input(dataframe: pd.DataFrame) -> None:
        """Raise a useful error when historical forecast features are missing."""
        if not isinstance(dataframe, pd.DataFrame):
            raise TypeError("Forecast data must be provided as a pandas DataFrame.")

        missing_features = [
            feature_name
            for feature_name in FORECAST_FEATURES
            if feature_name not in dataframe.columns
        ]
        if missing_features:
            missing_text = ", ".join(missing_features)
            raise ValueError(
                "Missing required forecast feature(s): "
                f"{missing_text}."
            )


def prepare_monthly_sales(transaction_data: pd.DataFrame) -> pd.DataFrame:
    """Clean transactions and aggregate valid positive sales by month."""
    required_columns = {"Invoice", "InvoiceDate", "Quantity", "Price"}
    missing_columns = required_columns - set(transaction_data.columns)
    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))
        raise ValueError(f"Transaction data is missing: {missing_text}.")

    cleaned_data = transaction_data.copy()
    cleaned_data["InvoiceDate"] = pd.to_datetime(
        cleaned_data["InvoiceDate"],
        errors="coerce",
    )
    cleaned_data["Quantity"] = pd.to_numeric(
        cleaned_data["Quantity"],
        errors="coerce",
    )
    cleaned_data["Price"] = pd.to_numeric(
        cleaned_data["Price"],
        errors="coerce",
    )
    cleaned_data = cleaned_data.dropna(
        subset=["InvoiceDate", "Quantity", "Price"]
    )
    cleaned_data = cleaned_data[
        (~cleaned_data["Invoice"].astype(str).str.startswith("C"))
        & (cleaned_data["Quantity"] > 0)
        & (cleaned_data["Price"] > 0)
    ].copy()
    cleaned_data["Sales"] = cleaned_data["Quantity"] * cleaned_data["Price"]

    monthly_sales = (
        cleaned_data.set_index("InvoiceDate")
        .resample("ME")["Sales"]
        .sum()
        .reset_index()
    )
    return monthly_sales


def create_forecast_features(monthly_sales: pd.DataFrame) -> pd.DataFrame:
    """Create leakage-free features from prior monthly sales history."""
    feature_data = monthly_sales.copy()
    feature_data["InvoiceDate"] = pd.to_datetime(feature_data["InvoiceDate"])
    feature_data = feature_data.sort_values("InvoiceDate").reset_index(drop=True)
    feature_data["Year"] = feature_data["InvoiceDate"].dt.year
    feature_data["Month"] = feature_data["InvoiceDate"].dt.month
    feature_data["Quarter"] = feature_data["InvoiceDate"].dt.quarter
    feature_data["Lag_1"] = feature_data["Sales"].shift(1)
    feature_data["Lag_2"] = feature_data["Sales"].shift(2)
    feature_data["Lag_3"] = feature_data["Sales"].shift(3)
    feature_data["Lag_6"] = feature_data["Sales"].shift(6)
    feature_data["RollingMean_3"] = feature_data["Sales"].rolling(3).mean().shift(1)
    feature_data["RollingMean_6"] = feature_data["Sales"].rolling(6).mean().shift(1)
    feature_data["RollingMean_12"] = feature_data["Sales"].rolling(12).mean().shift(1)

    return feature_data.dropna().reset_index(drop=True)


def create_next_month_features(monthly_sales: pd.DataFrame) -> tuple[pd.Timestamp, pd.DataFrame]:
    """Create the input features needed to forecast the month after history."""
    if len(monthly_sales) < 12:
        raise ValueError("At least 12 months of sales history are required.")

    ordered_sales = monthly_sales.sort_values("InvoiceDate").reset_index(drop=True)
    next_month = (
        pd.to_datetime(ordered_sales["InvoiceDate"].iloc[-1])
        + pd.offsets.MonthEnd(1)
    )
    sales_history = ordered_sales["Sales"]

    next_features = pd.DataFrame(
        [
            {
                "Year": next_month.year,
                "Month": next_month.month,
                "Quarter": next_month.quarter,
                "Lag_1": sales_history.iloc[-1],
                "Lag_2": sales_history.iloc[-2],
                "Lag_3": sales_history.iloc[-3],
                "Lag_6": sales_history.iloc[-6],
                "RollingMean_3": sales_history.iloc[-3:].mean(),
                "RollingMean_6": sales_history.iloc[-6:].mean(),
                "RollingMean_12": sales_history.iloc[-12:].mean(),
            }
        ]
    )
    return next_month, next_features

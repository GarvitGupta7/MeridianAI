"""Persistence helpers for additive RetailAI model artifacts."""
from __future__ import annotations

from pathlib import Path

import joblib

from .churn_pipeline import ChurnPipeline
from .forecast_engine import compare_forecast_models


def save_churn_pipeline(customers, directory: str | Path, random_state: int = 42):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    pipeline = ChurnPipeline(random_state).fit(customers)
    pipeline.save(directory / "retailai_churn_pipeline.joblib")
    pipeline.result.metrics.to_csv(directory / "retailai_churn_metrics.csv", index=False)
    pipeline.result.feature_importance.to_csv(directory / "retailai_churn_feature_importance.csv", index=False)
    return pipeline


def save_forecast_models(transactions, directory: str | Path, random_state: int = 42):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    metrics, meta = compare_forecast_models(transactions, random_state)
    metrics.to_csv(directory / "retailai_forecast_metrics.csv", index=False)
    for name, model in meta.get("models", {}).items():
        safe = name.lower().replace(" ", "_")
        joblib.dump(model, directory / f"retailai_forecast_{safe}.joblib")
    return metrics

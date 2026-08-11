"""Read persisted churn feature-importance results for API consumers."""

from __future__ import annotations

import pandas as pd

from src.config.paths import PROCESSED_DATA_DIR


FEATURE_IMPORTANCE_PATH = PROCESSED_DATA_DIR / "feature_importance.csv"


def load_churn_feature_importance() -> list[dict]:
    """Return globally ranked churn drivers produced by model evaluation.

    The artifact is generated alongside the trained churn model, ensuring API
    explanations refer to the same model version rather than recalculating a
    potentially inconsistent explanation at request time.
    """
    if not FEATURE_IMPORTANCE_PATH.exists():
        raise FileNotFoundError(
            "Churn feature-importance artifact was not found. Run model training first."
        )

    importance = pd.read_csv(FEATURE_IMPORTANCE_PATH)
    required_columns = {"Feature", "Importance"}
    if not required_columns.issubset(importance.columns):
        raise ValueError("Churn feature-importance artifact has an invalid schema.")

    ranked = importance.sort_values("Importance", ascending=False)
    return [
        {"feature": str(row.Feature), "importance": float(row.Importance)}
        for row in ranked.itertuples(index=False)
    ]

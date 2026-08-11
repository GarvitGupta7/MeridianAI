"""SHAP and model-prediction explanations for the additive ML layer."""
from __future__ import annotations

import pandas as pd


def explain_classifier(model, customers: pd.DataFrame, feature_names: list[str], max_rows: int = 25) -> pd.DataFrame:
    """Return local SHAP values when SHAP is available.

    The function intentionally accepts a fitted sklearn Pipeline and unwraps
    its feature/model steps so callers do not need to know implementation details.
    """
    try:
        import shap
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("SHAP is required for explainability") from exc
    transformed = model.named_steps["features"].transform(customers)
    core = model.named_steps["model"]
    if hasattr(core, "predict_proba"):
        explainer = shap.TreeExplainer(core) if hasattr(core, "tree_method") or hasattr(core, "estimators_") else shap.Explainer(core, transformed)
        values = explainer(transformed)
        values = values.values
        if values.ndim == 3:
            values = values[:, :, 1]
    else:
        explainer = shap.Explainer(core, transformed)
        values = explainer(transformed).values
    limited = values[:max_rows]
    rows = []
    for row_index, row in enumerate(limited):
        for feature, value in zip(feature_names, row):
            rows.append({"row": row_index, "feature": feature, "shap_value": float(value), "absolute_shap": abs(float(value))})
    return pd.DataFrame(rows).sort_values(["row", "absolute_shap"], ascending=[True, False]).reset_index(drop=True)

"""Training of customer-level purchase, churn, next-purchase, and spending models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_absolute_error, roc_auc_score


MODEL_FEATURES = ["recency_days", "frequency", "monetary_value", "avg_order_value", "tenure_days", "purchase_rate", "return_rate", "product_diversity"]


@dataclass
class PredictiveBundle:
    models: dict[str, Any]
    metrics: dict[str, float]


def train_predictive_models(customers: pd.DataFrame, random_state: int = 42) -> PredictiveBundle:
    """Train proxy future-outcome models from feature snapshots; replace targets with production labels when available."""
    if len(customers) < 20:
        return PredictiveBundle({}, {"status": "Need at least 20 customers for predictive models"})
    x = customers[MODEL_FEATURES].replace([np.inf, -np.inf], np.nan).fillna(0)
    purchase_target = ((customers["recency_days"] <= customers["recency_days"].median()) & (customers["frequency"] >= customers["frequency"].median())).astype(int)
    churn_target = (customers["churn_risk"] >= 60).astype(int)
    next_days = np.maximum(1, customers["recency_days"] * 0.65 + 30 / (customers["purchase_rate"] + .2))
    future_spend = customers["avg_order_value"] * np.maximum(1, customers["purchase_rate"]) * 3
    x_train, x_test, p_train, p_test = train_test_split(x, purchase_target, test_size=.25, random_state=random_state, stratify=purchase_target if purchase_target.nunique() > 1 else None)
    purchase = RandomForestClassifier(n_estimators=200, min_samples_leaf=2, random_state=random_state, class_weight="balanced").fit(x_train, p_train)
    churn = RandomForestClassifier(n_estimators=200, min_samples_leaf=2, random_state=random_state, class_weight="balanced").fit(x, churn_target)
    next_purchase = RandomForestRegressor(n_estimators=200, min_samples_leaf=2, random_state=random_state).fit(x, next_days)
    spending = RandomForestRegressor(n_estimators=200, min_samples_leaf=2, random_state=random_state).fit(x, future_spend)
    p_prob = purchase.predict_proba(x_test)[:, 1] if len(np.unique(p_test)) > 1 else np.zeros(len(p_test))
    metrics = {
        "purchase_accuracy": round(float(accuracy_score(p_test, purchase.predict(x_test))), 3),
        "purchase_auc": round(float(roc_auc_score(p_test, p_prob)), 3) if len(np.unique(p_test)) > 1 else float("nan"),
        "next_purchase_mae_in_sample": round(float(mean_absolute_error(next_days, next_purchase.predict(x))), 3),
        "spending_mae_in_sample": round(float(mean_absolute_error(future_spend, spending.predict(x))), 3),
    }
    return PredictiveBundle({"purchase": purchase, "churn": churn, "next_purchase": next_purchase, "spending": spending}, metrics)


def score_predictions(customers: pd.DataFrame, bundle: PredictiveBundle) -> pd.DataFrame:
    out = customers.copy()
    if not bundle.models:
        return out
    x = out[MODEL_FEATURES].replace([np.inf, -np.inf], np.nan).fillna(0)
    out["purchase_probability"] = bundle.models["purchase"].predict_proba(x)[:, 1].round(3)
    out["predicted_churn_probability"] = bundle.models["churn"].predict_proba(x)[:, 1].round(3)
    out["predicted_next_purchase_days"] = np.maximum(1, bundle.models["next_purchase"].predict(x)).round(1)
    out["predicted_90d_spend"] = np.maximum(0, bundle.models["spending"].predict(x)).round(2)
    return out

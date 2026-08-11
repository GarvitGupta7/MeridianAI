"""Dedicated churn model comparison and inference pipeline.

The module is additive to Meridian's existing predictive engine.  It provides
four independently evaluated classifiers and a production-safe preprocessing
pipeline for batch or API inference.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import StandardScaler

from .production_pipeline import DEFAULT_FEATURES, RetailFeatureSelector

try:
    from xgboost import XGBClassifier
except Exception:  # pragma: no cover - handled gracefully if optional dependency is unavailable
    XGBClassifier = None


@dataclass
class ChurnModelResult:
    models: dict[str, Pipeline]
    metrics: pd.DataFrame
    confusion_matrices: dict[str, list[list[int]]]
    feature_importance: pd.DataFrame
    feature_names: list[str]
    target_definition: str

    def best_model_name(self) -> str:
        if self.metrics.empty:
            raise ValueError("No churn models were trained")
        return str(self.metrics.sort_values(["roc_auc", "f1"], ascending=False).iloc[0]["model"])


class ChurnPipeline:
    """Train, compare, serialize and score production churn pipelines."""

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.feature_names = [
            feature for feature in DEFAULT_FEATURES
            if feature != "recency_days"
        ]
        self.result: ChurnModelResult | None = None

    @staticmethod
    def build_target(customers: pd.DataFrame) -> tuple[pd.Series, str]:
        if "churned" in customers.columns:
            return customers["churned"].astype(int), "Provided churned label"
        if "churn" in customers.columns:
            return customers["churn"].astype(int), "Provided churn label"
        if "churn_risk" not in customers.columns:
            raise ValueError("A churned/churn label or churn_risk column is required")
        # Fallback for Meridian's unlabeled retail datasets. This is explicitly
        # a proxy label, not a causal ground truth label.
        target = (
            (customers["churn_risk"].fillna(0) >= 65)
            | (customers["recency_days"].fillna(0) >= customers["recency_days"].quantile(.75))
        ).astype(int)
        return target, "Proxy label derived from churn_risk and upper-quartile recency"

    def _models(self) -> dict[str, Any]:
        models: dict[str, Any] = {
            "Logistic Regression": Pipeline([
                ("features", RetailFeatureSelector(self.feature_names)),
                ("scale", StandardScaler()),
                ("model", LogisticRegression(max_iter=1500, class_weight="balanced", random_state=self.random_state)),
            ]),
            "Decision Tree": Pipeline([
                ("features", RetailFeatureSelector(self.feature_names)),
                ("model", DecisionTreeClassifier(max_depth=7, min_samples_leaf=2, class_weight="balanced", random_state=self.random_state)),
            ]),
            "Random Forest": Pipeline([
                ("features", RetailFeatureSelector(self.feature_names)),
                ("model", RandomForestClassifier(n_estimators=300, min_samples_leaf=2, class_weight="balanced", random_state=self.random_state, n_jobs=-1)),
            ]),
        }
        if XGBClassifier is not None:
            models["XGBoost"] = Pipeline([
                ("features", RetailFeatureSelector(self.feature_names)),
                ("model", XGBClassifier(
                    n_estimators=250,
                    max_depth=5,
                    learning_rate=0.05,
                    subsample=0.9,
                    colsample_bytree=0.9,
                    eval_metric="logloss",
                    random_state=self.random_state,
                    n_jobs=2,
                )),
            ])
        return models

    def fit(self, customers: pd.DataFrame) -> ChurnModelResult:
        missing = [c for c in self.feature_names if c not in customers.columns]
        if missing:
            raise ValueError(f"Missing churn features: {', '.join(missing)}")
        y, target_definition = self.build_target(customers)
        if y.nunique() < 2:
            raise ValueError("Churn target must contain both classes")
        x_train, x_test, y_train, y_test = train_test_split(
            customers,
            y,
            test_size=.25,
            random_state=self.random_state,
            stratify=y,
        )
        fitted: dict[str, Pipeline] = {}
        rows: list[dict[str, Any]] = []
        matrices: dict[str, list[list[int]]] = {}
        importances: list[dict[str, Any]] = []
        for name, estimator in self._models().items():
            model = clone(estimator).fit(x_train, y_train)
            pred = model.predict(x_test)
            probability = model.predict_proba(x_test)[:, 1]
            fitted[name] = model
            rows.append({
                "model": name,
                "accuracy": round(float(accuracy_score(y_test, pred)), 4),
                "precision": round(float(precision_score(y_test, pred, zero_division=0)), 4),
                "recall": round(float(recall_score(y_test, pred, zero_division=0)), 4),
                "f1": round(float(f1_score(y_test, pred, zero_division=0)), 4),
                "roc_auc": round(float(roc_auc_score(y_test, probability)), 4),
            })
            matrices[name] = confusion_matrix(y_test, pred).astype(int).tolist()
            core = model.named_steps["model"]
            if hasattr(core, "feature_importances_"):
                importances.extend({"model": name, "feature": feature, "importance": float(value)} for feature, value in zip(self.feature_names, core.feature_importances_))
            elif hasattr(core, "coef_"):
                values = np.abs(core.coef_[0])
                importances.extend({"model": name, "feature": feature, "importance": float(value)} for feature, value in zip(self.feature_names, values))
        metrics = pd.DataFrame(rows).sort_values(["roc_auc", "f1"], ascending=False).reset_index(drop=True)
        importance = pd.DataFrame(importances)
        if not importance.empty:
            importance = importance.sort_values(["model", "importance"], ascending=[True, False]).reset_index(drop=True)
        self.result = ChurnModelResult(fitted, metrics, matrices, importance, self.feature_names, target_definition)
        return self.result

    def predict(self, customers: pd.DataFrame, model_name: str | None = None) -> pd.DataFrame:
        if self.result is None:
            raise RuntimeError("Fit the churn pipeline before prediction")
        selected = model_name or self.result.best_model_name()
        if selected not in self.result.models:
            raise ValueError(f"Unknown churn model: {selected}")
        model = self.result.models[selected]
        probability = model.predict_proba(customers)[:, 1]
        out = customers.copy()
        out["churn_probability"] = np.round(probability, 4)
        out["churn_prediction"] = (probability >= .5).astype(int)
        out["churn_risk_band"] = pd.cut(probability, [-.01, .30, .60, 1.01], labels=["Low", "Medium", "High"]).astype(str)
        return out

    def save(self, path) -> None:
        import joblib
        joblib.dump(self, path)

    @staticmethod
    def load(path) -> "ChurnPipeline":
        import joblib
        return joblib.load(path)

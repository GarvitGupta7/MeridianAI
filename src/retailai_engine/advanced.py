from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import AgglomerativeClustering, DBSCAN
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def advanced_segmentation(customers: pd.DataFrame) -> dict[str, pd.DataFrame]:
    required = ["recency_days", "frequency", "monetary_value"]
    if not all(c in customers.columns for c in required):
        return {"dbscan": pd.DataFrame(), "hierarchical": pd.DataFrame(), "outliers": pd.DataFrame()}
    frame = customers.copy()
    x = frame[required].replace([np.inf, -np.inf], np.nan).fillna(0)
    scaled = StandardScaler().fit_transform(x)
    n = len(frame)
    db = DBSCAN(eps=0.9, min_samples=max(4, min(8, n // 100 or 4))).fit_predict(scaled) if n >= 8 else np.full(n, -1)
    k = min(5, max(2, int(np.sqrt(max(n, 4) / 2)))) if n >= 4 else 1
    hierarchical = AgglomerativeClustering(n_clusters=k).fit_predict(scaled) if n >= k else np.zeros(n, dtype=int)
    iso = IsolationForest(contamination="auto", random_state=42).fit_predict(scaled) if n >= 10 else np.ones(n, dtype=int)
    return {
        "dbscan": pd.DataFrame({"customer_id": frame["customer_id"], "dbscan_cluster": db}),
        "hierarchical": pd.DataFrame({"customer_id": frame["customer_id"], "hierarchical_cluster": hierarchical}),
        "outliers": pd.DataFrame({"customer_id": frame["customer_id"], "outlier": iso == -1}),
    }


def model_comparison(customers: pd.DataFrame) -> pd.DataFrame:
    features = [
        c for c in [
            "monetary_value",
            "avg_order_value",
            "tenure_days",
            "purchase_rate",
            "product_diversity"
        ]
        if c in customers.columns
    ]

    if len(customers) < 20 or len(features) < 3:
        return pd.DataFrame(
            columns=["model", "accuracy", "precision", "recall", "f1"]
        )

    x = customers[features].replace(
        [np.inf, -np.inf], np.nan
    ).fillna(0)

    y = (customers["churn_risk"] >= 60).astype(int)

    if y.nunique() < 2:
        return pd.DataFrame(
            columns=["model", "accuracy", "precision", "recall", "f1"]
        )

    from sklearn.metrics import (
        accuracy_score,
        precision_score,
        recall_score,
        f1_score
    )
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LogisticRegression
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.pipeline import Pipeline

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y
    )

    models = {
        "Logistic Regression": Pipeline([
            ("scale", StandardScaler()),
            ("model", LogisticRegression(
                max_iter=1000,
                class_weight="balanced"
            ))
        ]),
        "Decision Tree": DecisionTreeClassifier(
            max_depth=6,
            min_samples_leaf=4,
            random_state=42,
            class_weight="balanced"
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            min_samples_leaf=3,
            random_state=42,
            class_weight="balanced",
            n_jobs=-1
        )
    }

    rows = []

    for name, model in models.items():
        model.fit(x_train, y_train)
        pred = model.predict(x_test)

        rows.append({
            "model": name,
            "accuracy": accuracy_score(y_test, pred),
            "precision": precision_score(
                y_test,
                pred,
                zero_division=0
            ),
            "recall": recall_score(
                y_test,
                pred,
                zero_division=0
            ),
            "f1": f1_score(
                y_test,
                pred,
                zero_division=0
            )
        })

    return pd.DataFrame(rows).round(3)

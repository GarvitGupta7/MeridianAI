"""Clustering algorithms and automatic quality-based K-Means selection."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, AgglomerativeClustering, KMeans
from sklearn.ensemble import IsolationForest
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score, silhouette_score
from sklearn.preprocessing import RobustScaler


FEATURE_COLUMNS = ["recency_days", "frequency", "monetary_value", "avg_order_value", "purchase_rate", "product_diversity", "return_rate"]


@dataclass
class ClusterResult:
    customers: pd.DataFrame
    evaluation: pd.DataFrame
    scaler: RobustScaler
    model: object
    method: str


def _metrics(matrix: np.ndarray, labels: np.ndarray) -> dict[str, float]:
    usable = labels != -1
    values, counts = np.unique(labels[usable], return_counts=True)
    if len(values) < 2 or len(matrix[usable]) <= len(values):
        return {"silhouette": np.nan, "davies_bouldin": np.nan, "calinski_harabasz": np.nan, "n_clusters": len(values), "noise_ratio": float((labels == -1).mean())}
    x, y = matrix[usable], labels[usable]
    return {"silhouette": float(silhouette_score(x, y)), "davies_bouldin": float(davies_bouldin_score(x, y)), "calinski_harabasz": float(calinski_harabasz_score(x, y)), "n_clusters": len(values), "noise_ratio": float((labels == -1).mean())}


def cluster_customers(customers: pd.DataFrame, min_clusters: int = 2, max_clusters: int = 8, random_state: int = 42) -> ClusterResult:
    if len(customers) < 4:
        raise ValueError("At least four customers are required for clustering")
    columns = [c for c in FEATURE_COLUMNS if c in customers.columns]
    x = customers[columns].replace([np.inf, -np.inf], np.nan).fillna(0).to_numpy(dtype=float)
    x[:, :3] = np.log1p(np.clip(x[:, :3], 0, None))
    scaler = RobustScaler()
    scaled = scaler.fit_transform(x)
    upper = min(max_clusters, len(customers) - 1)
    candidates = []
    models: dict[int, KMeans] = {}
    for k in range(min_clusters, upper + 1):
        model = KMeans(n_clusters=k, n_init=20, random_state=random_state).fit(scaled)
        metrics = _metrics(scaled, model.labels_)
        metrics.update({"method": "kmeans", "parameter": k})
        candidates.append(metrics)
        models[k] = model
    evaluation = pd.DataFrame(candidates)
    best_k = int(evaluation.sort_values(["silhouette", "davies_bouldin"], ascending=[False, True]).iloc[0]["parameter"])
    best_model = models[best_k]
    # Benchmark alternate algorithms for the dashboard and model governance.
    for name, model in [
        ("hierarchical", AgglomerativeClustering(n_clusters=best_k)),
        ("dbscan", DBSCAN(eps=1.2, min_samples=max(3, len(customers) // 30))),
    ]:
        labels = model.fit_predict(scaled)
        metrics = _metrics(scaled, labels)
        metrics.update({"method": name, "parameter": best_k if name == "hierarchical" else 1.2})
        evaluation = pd.concat([evaluation, pd.DataFrame([metrics])], ignore_index=True)
    out = customers.copy()
    out["cluster"] = best_model.labels_.astype(int)
    profile = out.groupby("cluster")["monetary_value"].mean().sort_values().rank(method="dense").astype(int)
    out["cluster_name"] = out["cluster"].map(lambda c: f"Segment {profile[c]}")
    detector = IsolationForest(contamination=min(.10, max(.02, 8 / len(customers))), random_state=random_state)
    out["anomaly_flag"] = (detector.fit_predict(scaled) == -1).astype(int)
    out["anomaly_score"] = (-detector.score_samples(scaled)).round(3)
    return ClusterResult(out, evaluation, scaler, best_model, "kmeans")

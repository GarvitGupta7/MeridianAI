"""Reusable ML evaluation helpers."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score


def classification_metrics(y_true, y_pred, probabilities=None) -> dict:
    result = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
    }
    if probabilities is not None and len(np.unique(y_true)) > 1:
        result["roc_auc"] = float(roc_auc_score(y_true, probabilities))
    return result

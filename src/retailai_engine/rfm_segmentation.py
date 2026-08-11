"""Explicit RFM segmentation built on Meridian customer features."""
from __future__ import annotations

import numpy as np
import pandas as pd


def rfm_segments(customers: pd.DataFrame) -> pd.DataFrame:
    required = ["customer_id", "recency_days", "frequency", "monetary_value"]
    missing = [c for c in required if c not in customers.columns]
    if missing:
        raise ValueError(f"Missing RFM columns: {', '.join(missing)}")
    out = customers[required].copy()
    out["r_score"] = pd.qcut(out["recency_days"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]).astype(int)
    out["f_score"] = pd.qcut(out["frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    out["m_score"] = pd.qcut(out["monetary_value"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]).astype(int)
    out["rfm_score"] = out[["r_score", "f_score", "m_score"]].sum(axis=1)
    out["rfm_segment"] = np.select(
        [out.rfm_score >= 13, out.rfm_score >= 10, out.rfm_score >= 7, out.rfm_score >= 5],
        ["Champions", "Loyal", "Potential", "At Risk"],
        default="Needs Attention",
    )
    return out

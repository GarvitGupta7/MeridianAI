"""Manager-facing summaries of persisted customer clusters."""

from __future__ import annotations

from src.segmentation.segment_predictor import load_customer_segments


def cluster_summary() -> list[dict]:
    """Return customer counts grouped by cluster and persona."""
    segments = load_customer_segments()
    summary = (
        segments.groupby(["Cluster", "Persona"], dropna=False)
        .size()
        .reset_index(name="customer_count")
        .sort_values("customer_count", ascending=False)
    )
    return [
        {
            "cluster": int(row.Cluster),
            "persona": str(row.Persona),
            "customer_count": int(row.customer_count),
        }
        for row in summary.itertuples(index=False)
    ]

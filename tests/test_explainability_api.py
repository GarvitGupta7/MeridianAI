"""Tests for the persisted churn explanation endpoint."""

from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_churn_feature_importance_is_ranked():
    """The endpoint should expose non-negative importances in rank order."""
    response = client.get("/explain/churn/feature-importance")

    assert response.status_code == 200
    importance = response.json()
    assert importance[0]["feature"] == "Recency"
    assert all(item["importance"] >= 0 for item in importance)

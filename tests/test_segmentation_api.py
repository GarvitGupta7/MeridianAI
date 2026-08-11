"""Tests for the persisted customer segmentation API."""

from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_cluster_summary_is_available():
    """Saved segmentation output should be exposed as a cluster summary."""
    response = client.get("/segments/summary")

    assert response.status_code == 200
    assert response.json()[0]["customer_count"] > 0


def test_known_customer_segment_is_available():
    """Known customers should retain their persisted segment assignment."""
    response = client.get("/segments/12346")

    assert response.status_code == 200
    assert response.json()["persona"] == "Churn Risk Customers"


def test_unknown_customer_segment_returns_not_found():
    """Unknown customers should receive a clear not-found response."""
    response = client.get("/segments/999999999")

    assert response.status_code == 404

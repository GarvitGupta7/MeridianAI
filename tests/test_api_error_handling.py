"""Tests for Meridian's global API error envelope."""

from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_invalid_churn_request_has_consistent_error_envelope():
    """Malformed API input should not return framework-specific error shapes."""
    response = client.post("/churn/predict", json={"Recency": 3})

    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"


def test_health_check_is_available():
    """Deployments need a lightweight endpoint that does not load request data."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"

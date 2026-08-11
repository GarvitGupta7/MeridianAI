"""
==========================================================
Meridian

Module:
Forecast API Tests

Description:
Verifies the forecasting API returns saved evaluation
results, model metrics and a manager-facing summary.

Author:
Garvit Gupta

Version:
2.0.0

Last Updated:
July 2026
==========================================================
"""

from fastapi.testclient import TestClient

from src.api.main import app


client = TestClient(app)


def test_forecast_summary_is_available():
    """The API should identify the best evaluated forecast model."""
    response = client.get("/forecast/summary")

    assert response.status_code == 200
    assert response.json()["best_model"] == "Linear Regression"


def test_forecast_results_are_available():
    """The API should return the historical forecast comparison data."""
    response = client.get("/forecast/results")

    assert response.status_code == 200
    assert len(response.json()) > 0


def test_forecast_model_metrics_are_available():
    """The API should return one metrics record per model."""
    response = client.get("/forecast/models")

    assert response.status_code == 200
    assert len(response.json()) == 5


def test_next_month_forecast_is_available():
    """The production pipeline should return a safe next-month forecast."""
    response = client.get("/forecast/next-month")

    assert response.status_code == 200
    assert response.json()["predicted_sales"] >= 0
    assert response.json()["confidence_status"] in {"low", "review"}


def test_future_forecast_supports_a_bounded_batch_horizon():
    """Forecasts should support a bounded future horizon with uncertainty bands."""
    response = client.get("/forecast/future?months=2")

    assert response.status_code == 200
    forecasts = response.json()
    assert len(forecasts) == 2
    assert forecasts[0]["lower_bound"] <= forecasts[0]["predicted_sales"]
    assert forecasts[0]["upper_bound"] >= forecasts[0]["predicted_sales"]

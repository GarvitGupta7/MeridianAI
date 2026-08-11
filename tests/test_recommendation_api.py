"""
==========================================================
Meridian

Module:
Recommendation API Tests

Description:
Verifies personalised product recommendations, cold-start
fallback behaviour and recommendation coverage metrics.

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


def test_recommendation_summary_is_available():
    """The API should return recommendation coverage metrics."""
    response = client.get("/recommendations/summary")

    assert response.status_code == 200
    assert response.json()["customers_covered"] > 0


def test_known_customer_recommendations_are_available():
    """Known customers should receive saved hybrid recommendations."""
    response = client.get("/recommendations/12346")

    assert response.status_code == 200
    assert len(response.json()["recommendations"]) > 0


def test_unknown_customer_receives_cold_start_recommendations():
    """Unknown customers should receive popular products instead of an error."""
    response = client.get("/recommendations/999999999")

    assert response.status_code == 200
    assert response.json()["strategy"] == "popular-product cold-start fallback"


def test_popular_products_are_available_for_discovery():
    """Product discovery should expose the same ranked cold-start fallback."""
    response = client.get("/recommendations/popular?top_n=3")

    assert response.status_code == 200
    assert len(response.json()["recommendations"]) == 3

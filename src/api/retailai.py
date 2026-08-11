"""
MeridianAI API extensions.

All endpoints are additive. Existing MeridianAI routes remain unchanged.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from src.retailai_engine.churn_pipeline import ChurnPipeline
from src.retailai_engine.explainability import explain_classifier
from src.retailai_engine.forecast_engine import (
    compare_forecast_models,
    forecast_with_uncertainty,
)
from src.retailai_engine.recommendation_engine import AdvancedRecommendationEngine
from src.retailai_engine.rfm_segmentation import rfm_segments
from src.retailai_engine.advanced import advanced_segmentation, model_comparison

router = APIRouter(tags=["MeridianAI Advanced ML"])


def _result():
    from src.api.main import _state

    if "result" not in _state:
        raise HTTPException(404, "No analysis is loaded.")

    return _state["result"]


def _customers():
    return _result()["customers"]


def _transactions():
    return _result()["transactions"]


def _records(data, limit=None):
    if hasattr(data, "head") and limit is not None:
        data = data.head(limit)

    if hasattr(data, "to_dict"):
        return data.to_dict(orient="records")

    return data


# ============================================================
# ANALYTICS
# ============================================================

@router.get("/analytics/dashboard", tags=["Analytics"])
def analytics_dashboard():
    customers = _customers()

    return {
        "customer_count": int(len(customers)),
        "total_revenue": float(
            customers["TotalSpent"].sum()
        ) if "TotalSpent" in customers.columns else 0.0,
        "average_spent": float(
            customers["TotalSpent"].mean()
        ) if "TotalSpent" in customers.columns else 0.0,
        "average_frequency": float(
            customers["Frequency"].mean()
        ) if "Frequency" in customers.columns else 0.0,
        "average_recency": float(
            customers["Recency"].mean()
        ) if "Recency" in customers.columns else 0.0,
    }


@router.get("/analytics/revenue", tags=["Analytics"])
def analytics_revenue():
    customers = _customers()

    if "TotalSpent" not in customers.columns:
        return {"total_revenue": 0.0}

    return {
        "total_revenue": float(customers["TotalSpent"].sum()),
        "average_revenue_per_customer": float(
            customers["TotalSpent"].mean()
        ),
    }


@router.get("/analytics/recency", tags=["Analytics"])
def analytics_recency():
    customers = _customers()

    if "Recency" not in customers.columns:
        return {"average_recency": 0.0}

    return {
        "average_recency": float(customers["Recency"].mean()),
        "median_recency": float(customers["Recency"].median()),
        "minimum_recency": float(customers["Recency"].min()),
        "maximum_recency": float(customers["Recency"].max()),
    }


@router.get("/analytics/tiers", tags=["Analytics"])
def analytics_tiers():
    customers = _customers()

    if "Tier" not in customers.columns:
        return {}

    return customers["Tier"].value_counts().to_dict()


@router.get("/analytics/personas", tags=["Analytics"])
def analytics_personas():
    customers = _customers()

    if "Persona" not in customers.columns:
        return {}

    return customers["Persona"].value_counts().to_dict()


@router.get("/analytics/clusters", tags=["Analytics"])
def analytics_clusters():
    customers = _customers()

    if "Cluster" not in customers.columns:
        return {}

    return customers["Cluster"].value_counts().to_dict()


@router.get("/analytics/average-spent", tags=["Analytics"])
def analytics_average_spent():
    customers = _customers()

    if "TotalSpent" not in customers.columns:
        return {"average_spent": 0.0}

    return {
        "average_spent": float(customers["TotalSpent"].mean())
    }


@router.get("/analytics/average-frequency", tags=["Analytics"])
def analytics_average_frequency():
    customers = _customers()

    if "Frequency" not in customers.columns:
        return {"average_frequency": 0.0}

    return {
        "average_frequency": float(customers["Frequency"].mean())
    }


# ============================================================
# CUSTOMERS
# ============================================================

@router.get("/customers/count", tags=["Customers"])
def customer_count():
    return {"count": len(_customers())}


@router.get("/customers/high-value", tags=["Customers"])
def high_value_customers(limit: int = 100):
    customers = _customers()

    if "TotalSpent" not in customers.columns:
        return []

    return _records(
        customers.sort_values("TotalSpent", ascending=False),
        limit,
    )


@router.get("/customers/high-churn", tags=["Customers"])
def high_churn_customers(limit: int = 100):
    result = _result()
    customers = result["customers"].copy()

    pipeline = ChurnPipeline().fit(customers)
    predictions = pipeline.predict(customers)

    if "ChurnProbability" in predictions.columns:
        predictions = predictions.sort_values(
            "ChurnProbability",
            ascending=False,
        )

    return _records(predictions, limit)


@router.get("/customers/{customer_id}", tags=["Customers"])
def customer_detail(customer_id: str):
    customers = _customers()

    if "CustomerID" not in customers.columns:
        raise HTTPException(404, "CustomerID column not found.")

    matches = customers[
        customers["CustomerID"].astype(str) == str(customer_id)
    ]

    if matches.empty:
        raise HTTPException(404, "Customer not found.")

    return matches.iloc[0].to_dict()


# ============================================================
# SEGMENTATION
# ============================================================

@router.get("/segments/summary", tags=["Segmentation"])
def segments_summary():
    customers = _customers()

    output = {
        "customer_count": len(customers)
    }

    for column in [
        "Cluster",
        "DBSCAN_Cluster",
        "Hierarchical_Cluster",
        "Persona",
        "Tier",
    ]:
        if column in customers.columns:
            output[column] = customers[column].value_counts().to_dict()

    return output


@router.get("/segments/{customer_id}", tags=["Segmentation"])
def customer_segment(customer_id: str):
    customers = _customers()

    if "CustomerID" not in customers.columns:
        raise HTTPException(404, "CustomerID column not found.")

    matches = customers[
        customers["CustomerID"].astype(str) == str(customer_id)
    ]

    if matches.empty:
        raise HTTPException(404, "Customer not found.")

    customer = matches.iloc[0]

    return {
        "customer_id": str(customer_id),
        "cluster": customer.get("Cluster"),
        "dbscan_cluster": customer.get("DBSCAN_Cluster"),
        "hierarchical_cluster": customer.get("Hierarchical_Cluster"),
        "persona": customer.get("Persona"),
        "tier": customer.get("Tier"),
        "score": customer.get("CustomerScore"),
    }


@router.get("/segmentation/rfm", tags=["Segmentation"])
def segmentation_rfm(limit: int = 100):
    return _records(rfm_segments(_customers()), limit)


@router.get("/segmentation/advanced", tags=["Segmentation"])
def segmentation_advanced():
    result = advanced_segmentation(_customers())

    return {
        key: value.to_dict(orient="records")
        for key, value in result.items()
    }


# ============================================================
# CHURN
# ============================================================

@router.get("/churn/compare", tags=["Churn Prediction"])
def churn_compare():
    result = _result()

    pipeline = ChurnPipeline().fit(result["customers"])

    return {
        "target_definition": pipeline.result.target_definition,
        "best_model": pipeline.result.best_model_name(),
        "metrics": pipeline.result.metrics.to_dict(
            orient="records"
        ),
        "confusion_matrices": pipeline.result.confusion_matrices,
    }


@router.get("/churn/predict", tags=["Churn Prediction"])
def churn_predict(
    limit: int = 100,
    model: str | None = None,
):
    result = _result()

    pipeline = ChurnPipeline().fit(result["customers"])

    return pipeline.predict(
        result["customers"].head(limit),
        model,
    ).to_dict(orient="records")


@router.get("/churn/feature-importance", tags=["Churn Prediction"])
def churn_feature_importance():
    result = _result()

    pipeline = ChurnPipeline().fit(result["customers"])

    return pipeline.result.feature_importance.to_dict(
        orient="records"
    )


@router.get("/churn/explain", tags=["Explainability"])
def churn_explain(
    limit: int = 10,
    model: str | None = None,
):
    result = _result()

    pipeline = ChurnPipeline().fit(result["customers"])

    selected = model or pipeline.result.best_model_name()

    explanation = explain_classifier(
        pipeline.result.models[selected],
        result["customers"].head(limit),
        pipeline.feature_names,
        limit,
    )

    return explanation.to_dict(orient="records")


# ============================================================
# FORECASTING
# ============================================================

@router.get("/forecast/summary", tags=["Forecasting"])
def forecast_summary():
    result = _result()

    forecast = result.get("sales_forecast")

    if forecast is None:
        return {}

    return {
        "rows": len(forecast),
        "columns": list(forecast.columns),
        "latest": forecast.tail(1).to_dict(
            orient="records"
        ),
    }


@router.get("/forecast/results", tags=["Forecasting"])
def forecast_results(limit: int = 100):
    result = _result()

    forecast = result.get("sales_forecast")

    if forecast is None:
        return []

    return _records(forecast, limit)


@router.get("/forecast/models", tags=["Forecasting"])
def forecast_models():
    result = _result()

    metrics, _ = compare_forecast_models(
        result["transactions"]
    )

    return metrics.to_dict(orient="records")


@router.get("/forecast/next-month", tags=["Forecasting"])
def forecast_next_month():
    result = _result()

    forecast = result.get("sales_forecast")

    if forecast is None or len(forecast) == 0:
        return {}

    return forecast.tail(1).to_dict(
        orient="records"
    )[0]


@router.get("/forecast/future", tags=["Forecasting"])
def forecast_future(periods: int = 3):
    result = _result()

    return forecast_with_uncertainty(
        result["transactions"],
        periods,
    ).to_dict(orient="records")


@router.get("/forecast/compare", tags=["Forecasting"])
def forecast_compare():
    result = _result()

    metrics, _ = compare_forecast_models(
        result["transactions"]
    )

    return metrics.to_dict(orient="records")


@router.get("/forecast/uncertainty", tags=["Forecasting"])
def forecast_uncertainty(periods: int = 3):
    result = _result()

    return forecast_with_uncertainty(
        result["transactions"],
        periods,
    ).to_dict(orient="records")


# ============================================================
# RECOMMENDATIONS
# ============================================================

@router.get("/recommendations/summary", tags=["Recommendations"])
def recommendation_summary():
    result = _result()

    engine = AdvancedRecommendationEngine(
        result["transactions"]
    )

    return {
        "customer_count": len(engine.customer_similarity),
        "product_count": len(engine.product_similarity),
        "popular_products": engine.popular_products(10),
    }


@router.get("/recommendations/popular", tags=["Recommendations"])
def popular_recommendations(limit: int = 10):
    result = _result()

    engine = AdvancedRecommendationEngine(
        result["transactions"]
    )

    return engine.popular_products(limit)


@router.get(
    "/recommendations/{customer_id}",
    tags=["Recommendations"],
)
def customer_recommendations_legacy(
    customer_id: str,
    limit: int = 10,
):
    result = _result()

    engine = AdvancedRecommendationEngine(
        result["transactions"]
    )

    return engine.recommend(
        customer_id,
        limit,
    )


@router.get(
    "/recommendations/customer/{customer_id}",
    tags=["Recommendations"],
)
def customer_recommendations(
    customer_id: str,
    limit: int = 10,
):
    result = _result()

    engine = AdvancedRecommendationEngine(
        result["transactions"]
    )

    return engine.recommend(
        customer_id,
        limit,
    )


@router.get(
    "/recommendations/customer/{customer_id}/similar",
    tags=["Recommendations"],
)
def similar_customers(
    customer_id: str,
    limit: int = 10,
):
    result = _result()

    engine = AdvancedRecommendationEngine(
        result["transactions"]
    )

    return engine.similar_customers(
        customer_id,
        limit,
    )


@router.get(
    "/recommendations/product/{product_id}/similar",
    tags=["Recommendations"],
)
def similar_products(
    product_id: str,
    limit: int = 10,
):
    result = _result()

    engine = AdvancedRecommendationEngine(
        result["transactions"]
    )

    return engine.similar_products(
        product_id,
        limit,
    )


# ============================================================
# MODEL COMPARISON
# ============================================================

@router.get("/models/comparison", tags=["Advanced ML"])
def models_comparison():
    result = _result()

    return model_comparison(
        result["customers"]
    ).to_dict(orient="records")
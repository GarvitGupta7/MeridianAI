"""FastAPI model-serving interface."""
from __future__ import annotations

import io

import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from .config import settings
from .database import RetailRepository
from .service import RetailSegmentationService
from fastapi import FastAPI
from src.api.retailai import router as retailai_router

app = FastAPI(
    title="Meridian API",
    version="1.0.0",
    description="Retail customer analytics, segments, forecasts, and recommendations."
)

app.include_router(retailai_router)
repository = RetailRepository(settings.database_path)
service = RetailSegmentationService()


class RecommendationRequest(BaseModel):
    customer_id: str
    limit: int = Field(default=5, ge=1, le=20)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "database_tables": repository.tables()}


@app.get("/summary")
def summary() -> dict:
    try:
        customers_frame = repository.load_frame("customers")
        transactions = repository.load_frame("transactions")
    except Exception as exc:
        raise HTTPException(503, "No trained dataset. Run the pipeline first.") from exc
    return {
        "customers": len(customers_frame),
        "revenue": round(float(transactions.revenue.sum()), 2),
        "orders": int(transactions.invoice_id.nunique()),
        "at_risk_customers": int((customers_frame.persona == "At-risk customers").sum()),
        "average_health_score": round(float(customers_frame.health_score.mean()), 1),
    }


@app.get("/customers")
def customers(persona: str | None = None, cluster: int | None = None, limit: int = 100) -> list[dict]:
    try:
        frame = repository.load_frame("customers")
    except Exception as exc:
        raise HTTPException(503, "No trained dataset. Run `python -m retail_segmentation.main --demo` first.") from exc
    if persona:
        frame = frame[frame.persona == persona]
    if cluster is not None:
        frame = frame[frame.cluster == cluster]
    return frame.head(min(limit, 1000)).to_dict(orient="records")


@app.get("/customers/{customer_id}")
def customer(customer_id: str) -> dict:
    rows = customers(limit=1000)
    found = next((row for row in rows if str(row["customer_id"]) == str(customer_id)), None)
    if not found:
        raise HTTPException(404, "Customer not found")
    return found


@app.get("/clusters/evaluation")
def cluster_evaluation() -> list[dict]:
    try:
        return repository.load_frame("cluster_evaluation").to_dict(orient="records")
    except Exception as exc:
        raise HTTPException(503, "No cluster evaluation available") from exc


@app.get("/campaigns")
def campaigns(priority: str | None = None, limit: int = 100) -> list[dict]:
    try:
        frame = repository.load_frame("campaign_recommendations")
    except Exception as exc:
        raise HTTPException(503, "No campaign recommendations available") from exc
    if priority:
        frame = frame[frame.priority.str.lower() == priority.lower()]
    return frame.head(min(limit, 1000)).to_dict(orient="records")


@app.get("/analytics/cohort-retention")
def retention() -> list[dict]:
    try:
        return repository.load_frame("cohort_retention").to_dict(orient="records")
    except Exception as exc:
        raise HTTPException(503, "No cohort retention data available") from exc


@app.post("/analyze")
async def analyze_file(file: UploadFile = File(...)) -> dict:
    """Analyze an uploaded CSV/XLSX transaction export."""
    filename = (file.filename or "").lower()
    content = await file.read()
    try:
        if filename.endswith(".csv"):
            frame = pd.read_csv(io.BytesIO(content))
        elif filename.endswith((".xlsx", ".xls")):
            frame = pd.read_excel(io.BytesIO(content))
        elif filename.endswith(".json"):
            frame = pd.read_json(io.BytesIO(content))
        else:
            raise ValueError("Upload a CSV, XLSX, XLS, or JSON file")
        result = service.run(frame, persist=True)
        return {"message": "Analysis completed", "summary": result["summary"], "rows_processed": len(result["transactions"])}
    except Exception as exc:
        raise HTTPException(422, f"Unable to process file: {exc}") from exc


@app.get("/forecast/sales")
def sales_forecast() -> list[dict]:
    try:
        return repository.load_frame("sales_forecast").to_dict(orient="records")
    except Exception as exc:
        raise HTTPException(503, "No sales forecast available") from exc


@app.get("/models/explanations")
def model_explanations() -> list[dict]:
    try:
        return repository.load_frame("model_explanations").to_dict(orient="records")
    except Exception as exc:
        raise HTTPException(503, "No model explanations available") from exc


@app.get("/data-quality")
def data_quality() -> dict:
    try:
        return {"comparison": repository.load_frame("data_quality_comparison").to_dict(orient="records"), "column_profile": repository.load_frame("cleaned_column_profile").to_dict(orient="records")}
    except Exception as exc:
        raise HTTPException(503, "No data-quality report available") from exc


@app.post("/recommendations/products")
def product_recommendations(request: RecommendationRequest) -> list[dict]:
    try:
        return service.load_recommendation_engine().recommend_products(request.customer_id, request.limit)
    except Exception as exc:
        raise HTTPException(503, "No transaction history available") from exc


@app.get("/recommendations/cross-sell/{product_id}")
def cross_sell(product_id: str, limit: int = 5) -> list[dict]:
    return service.load_recommendation_engine().cross_sell(product_id, limit)


@app.get("/recommendations/upsell/{product_id}")
def upsell(product_id: str, limit: int = 3) -> list[dict]:
    return service.load_recommendation_engine().upsell(product_id, limit)

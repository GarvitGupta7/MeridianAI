# MeridianAI API reference

## Runtime

- FastAPI application: `src.retail_segmentation.api:app`
- Launcher: `python -m src.api.run`
- Development base URL: `http://127.0.0.1:8000`
- API version: `1.0.0`
- Swagger UI: `/docs`
- OpenAPI document: `/openapi.json`
- Authentication: none in the current implementation
- Total application operations: **47** — 45 GET and 2 POST

The canonical application includes the router from `src/api/retailai.py` without a prefix. Consequently, advanced routes are mounted directly at paths such as `/analytics/dashboard`, not `/retailai/analytics/dashboard`.

## Operating assumptions

Most routes read persisted frames from the configured SQLAlchemy database or create the shared service result. If the pipeline has not been run and the required bundled database/artifacts are unavailable, data-dependent routes can return `503`.

Common responses:

| Status | Meaning |
|---:|---|
| 200 | Successful request |
| 404 | Requested customer or entity was not found |
| 422 | FastAPI validation failure or uploaded input could not be processed |
| 503 | Required trained data, table, transaction history, or model output is unavailable |

This is an internal project API. It currently has no authentication, authorization, rate limiting, or public deployment hardening.

## Response-contract status

Most handlers currently annotate broad `dict` or `list[dict]` return types instead of explicit Pydantic response models. Swagger therefore cannot provide a strong, versioned schema for every successful response. The shapes in this document reflect current code and database columns but are not yet a compatibility guarantee.

Representative current responses:

```json
{
  "status": "ok",
  "database_tables": ["customers", "transactions"]
}
```

```json
{
  "customers": 240,
  "revenue": 438016.66,
  "orders": 749,
  "at_risk_customers": 58,
  "average_health_score": 66.0
}
```

```json
{
  "customer_count": 240,
  "total_revenue": 438016.66,
  "average_spent": 1825.07,
  "average_frequency": 3.12,
  "average_recency": 52.4
}
```

Values above illustrate the response fields; live values depend on the active persisted dataset. Customer, campaign, forecast, cohort, and explanation list items follow the columns in [DATABASE_DICTIONARY.md](DATABASE_DICTIONARY.md).

Before external clients depend on this API, add named request/response models, examples, field descriptions, nullability, units, error models, and an explicit compatibility/version policy.

## Health, ingestion, and summary

| Method | Path | Parameters/body | Purpose |
|---|---|---|---|
| GET | `/health` | — | Service status and available database tables |
| GET | `/summary` | — | Portfolio customer, revenue, order, risk, and health summary |
| POST | `/analyze` | Multipart field `file` | Analyze and persist a CSV, XLSX, XLS, or JSON transaction export |

Example:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
curl.exe -X POST http://127.0.0.1:8000/analyze -F "file=@data/raw/transactions.csv"
```

`POST /analyze` persists the processed result. This differs from an uploaded Streamlit session analysis, which runs with `persist=False`.

## Customers

| Method | Path | Parameters | Purpose |
|---|---|---|---|
| GET | `/customers` | `persona`, `cluster`, `limit=100` | List persisted customers, optionally filtered; limit is capped at 1,000 |
| GET | `/customers/{customer_id}` | Path: `customer_id` | Retrieve a customer from the first 1,000 customer rows |
| GET | `/customers/count` | — | Count customers in the shared service result |
| GET | `/customers/high-value` | `limit=100` | Highest-value customers |
| GET | `/customers/high-churn` | `limit=100` | Customers with the highest predicted or scored churn risk |

## Analytics

| Method | Path | Parameters | Purpose |
|---|---|---|---|
| GET | `/analytics/dashboard` | — | Aggregated dashboard metrics |
| GET | `/analytics/revenue` | — | Revenue summary |
| GET | `/analytics/recency` | — | Average recency summary |
| GET | `/analytics/tiers` | — | Customer tier distribution |
| GET | `/analytics/personas` | — | Persona distribution |
| GET | `/analytics/clusters` | — | Cluster distribution |
| GET | `/analytics/average-spent` | — | Average customer monetary value |
| GET | `/analytics/average-frequency` | — | Average customer frequency |
| GET | `/analytics/cohort-retention` | — | Persisted cohort-retention records |

## Segmentation and clustering

| Method | Path | Parameters | Purpose |
|---|---|---|---|
| GET | `/segments/summary` | — | Summary by segment/cluster |
| GET | `/segments/{customer_id}` | Path: `customer_id` | Segment record for one customer |
| GET | `/segmentation/rfm` | `limit=100` | RFM segmentation records |
| GET | `/segmentation/advanced` | — | DBSCAN, hierarchical, and anomaly outputs |
| GET | `/clusters/evaluation` | — | Persisted cluster-evaluation metrics |

## Churn prediction and explainability

| Method | Path | Parameters | Purpose |
|---|---|---|---|
| GET | `/churn/compare` | — | Compare supported churn classifiers |
| GET | `/churn/predict` | `limit=100`, `model` | Batch churn predictions using the selected or best model |
| GET | `/churn/feature-importance` | — | Churn model feature importance or coefficient magnitude |
| GET | `/churn/explain` | `limit=10`, `model` | Per-customer churn explanations |

Supported comparison estimators are Logistic Regression, Decision Tree, Random Forest, and XGBoost when its import succeeds. Proxy churn targets must not be treated as observed causal outcomes.

## Forecasting

| Method | Path | Parameters | Purpose |
|---|---|---|---|
| GET | `/forecast/summary` | — | Forecast status and summary |
| GET | `/forecast/results` | `limit=100` | Forecast result rows |
| GET | `/forecast/models` | — | Forecast model metrics |
| GET | `/forecast/next-month` | — | Next-month forecast |
| GET | `/forecast/future` | `periods=3` | Multi-period forecast with uncertainty |
| GET | `/forecast/compare` | — | Linear Regression, Random Forest, and optional XGBoost comparison |
| GET | `/forecast/uncertainty` | `periods=3` | Forecast intervals |
| GET | `/forecast/sales` | — | Persisted sales-forecast rows |

## Campaigns

| Method | Path | Parameters | Purpose |
|---|---|---|---|
| GET | `/campaigns` | `priority`, `limit=100` | Persisted campaign recommendations, optionally filtered by priority |

Campaign records can contain priority, strategy, recommended action, offer, channel, incentive, reason, and opportunity score.

## Recommendations

| Method | Path | Parameters/body | Purpose |
|---|---|---|---|
| GET | `/recommendations/summary` | — | Recommendation-engine summary |
| GET | `/recommendations/popular` | `limit=10` | Popular product recommendations |
| GET | `/recommendations/{customer_id}` | Path: `customer_id`; `limit=10` | Legacy customer recommendation route |
| GET | `/recommendations/customer/{customer_id}` | Path: `customer_id`; `limit=10` | Customer product recommendations |
| GET | `/recommendations/customer/{customer_id}/similar` | Path: `customer_id`; `limit=10` | Similar customers |
| GET | `/recommendations/product/{product_id}/similar` | Path: `product_id`; `limit=10` | Similar products |
| POST | `/recommendations/products` | JSON: `customer_id`, `limit=5` | Product recommendations; limit must be 1–20 |
| GET | `/recommendations/cross-sell/{product_id}` | Path: `product_id`; `limit=5` | Cross-sell products |
| GET | `/recommendations/upsell/{product_id}` | Path: `product_id`; `limit=3` | Upsell products |

Example request:

```powershell
$body = @{ customer_id = "12345"; limit = 5 } | ConvertTo-Json
Invoke-RestMethod `
  -Method Post `
  -Uri http://127.0.0.1:8000/recommendations/products `
  -ContentType application/json `
  -Body $body
```

## Models and data quality

| Method | Path | Parameters | Purpose |
|---|---|---|---|
| GET | `/models/comparison` | — | Advanced model-comparison output |
| GET | `/models/explanations` | — | Persisted model explanations |
| GET | `/data-quality` | — | Cleaning comparison and cleaned-column profile |

## OpenAPI verification

When the application is running, verify the generated surface with:

```powershell
$schema = Invoke-RestMethod http://127.0.0.1:8000/openapi.json
$operations = foreach ($path in $schema.paths.PSObject.Properties) {
    foreach ($method in $path.Value.PSObject.Properties) {
        if ($method.Name -in @("get", "post", "put", "patch", "delete")) {
            "{0} {1}" -f $method.Name.ToUpper(), $path.Name
        }
    }
}
$operations.Count
$operations | Sort-Object
```

The expected count for the documented code state is `47`.

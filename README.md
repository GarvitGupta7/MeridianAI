# Meridian

> Retail intelligence for customer growth, retention, and sales planning.

An end-to-end, self-service Python platform for customer analytics, segmentation, prediction, recommendations, and retail decision support.

## Self-service company data upload

Any retailer can use the platform without changing source code:

1. Start the dashboard with `streamlit run dashboard.py`.
2. Upload a CSV, XLSX, XLS, or JSON transaction export from the Data controls section below the main workspace header.
3. The portal detects common retail fields automatically (such as `Order ID`, `CustomerID`, `Date`, `Qty`, and `Sales Price`). It only asks for column mapping if a required concept is ambiguous or unavailable.
4. Select **Run analysis**. The portal first runs EDA and data-quality checks, cleans duplicate/malformed/invalid transaction records, then trains models and makes insights and cleaned-data downloads available.

Optional product, product-description, and country fields enrich recommendations and customer behavior features.

## Included capabilities

- **Data engineering:** data contract validation, cleaning, preprocessing, feature engineering, quality reporting.
- **Customer analytics:** RFM, CLV estimate, explainable churn risk, health score, and six business personas.
- **Machine learning:** automatic K-Means cluster selection plus DBSCAN and hierarchical benchmarks. Evaluation includes silhouette, Davies–Bouldin, and Calinski–Harabasz scores.
- **Predictive Engine:** generate an individual customer report by Customer ID or a representative customer prediction from filters; reports include purchase likelihood, churn likelihood, next-purchase timing, 90-day spend, customer attributes, and a decision summary. Detailed visual analysis is kept on the separate Customer Visuals page.
- **Recommendations:** history-based product recommendations, basket cross-sells, and price-tier upsells.
- **Action planning:** campaign recommendations by customer priority and persona, plus monthly cohort-retention analytics.
- **Retail operations:** customer tiers, anomaly detection, three-month revenue forecast, and global model feature importance.
- **Automatic EDA:** dataset shape, data types, missing values, duplicates, numeric outliers, monthly revenue, top products, country performance, and a before-versus-after cleaning report.
- **Reporting-first workspace:** Overview, Customers, Predictive Engine, Campaigns, Sales Planning, Data Quality, and Model Trust are report-oriented pages with decision tables, written interpretation, KPIs, and downloadable outputs. **Customer Visuals** is the dedicated visualization workspace for charts, distributions, relationships, and exploratory analysis.
- **Applications:** Streamlit + Plotly dashboard, FastAPI REST API, SQLite persistence (with a documented PostgreSQL extension point).
- **Delivery:** Docker Compose, GitHub Actions CI, tests, architecture, report, and requirements.

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:PYTHONPATH = "src"
python -m retail_segmentation.main --demo
streamlit run dashboard.py
```

To process your own data, replace the final command with:

```powershell
python -m retail_segmentation.main --input path\to\transactions.csv
```

The CSV must include `invoice_id`, `customer_id`, `invoice_date`, `quantity`, and `unit_price`. Optional fields: `stock_code`, `product_name`, `country`. Common names such as `InvoiceNo`, `CustomerID`, `InvoiceDate`, `UnitPrice`, and `StockCode` are normalized automatically.

## Run the API

```powershell
$env:PYTHONPATH = "src"
uvicorn retail_segmentation.api:app --reload
```

Open [interactive API documentation](http://127.0.0.1:8000/docs). Key endpoints include:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Service/data availability |
| GET | `/customers?persona=&cluster=` | Filter customer intelligence |
| GET | `/customers/{customer_id}` | Customer profile and scores |
| GET | `/clusters/evaluation` | Clustering quality measurements |
| GET | `/summary` | Executive KPI summary |
| GET | `/campaigns?priority=Critical` | Prioritized retention and growth actions |
| GET | `/analytics/cohort-retention` | Monthly cohort-retention data |
| POST | `/analyze` | Upload and analyze a CSV/XLSX transaction export |
| GET | `/forecast/sales` | Next-three-month sales forecast |
| GET | `/models/explanations` | Feature importance for predictive models |
| GET | `/data-quality` | Cleaning comparison and column-level EDA profile |
| POST | `/recommendations/products` | Personalized product recommendations |
| GET | `/recommendations/cross-sell/{product_id}` | Basket recommendations |
| GET | `/recommendations/upsell/{product_id}` | Higher-value alternatives |

## Database configuration

SQLite is the default (`artifacts/retail_segmentation.db`). To connect PostgreSQL instead, set `DATABASE_URL` before running the pipeline/API:

```powershell
$env:DATABASE_URL = "postgresql+psycopg://user:password@localhost:5432/retail"
```

## Validation and tests

```powershell
$env:PYTHONPATH = "src"
pytest -q
```

See [architecture](docs/architecture.md) and the [project report](docs/project_report.md) for the design and operating guidance.

## Project layout

```text
src/retail_segmentation/  data, analytics, models, recommendations, API
dashboard.py              Streamlit application
tests/                    pipeline tests
docs/                     architecture and report
.github/workflows/        CI pipeline
```

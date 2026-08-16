# Notebook-to-production traceability

## Purpose

The notebooks are historical experiment and analysis assets. Production behavior is defined by `src/`, `dashboard.py`, persisted artifacts, and tests—not by notebook output cells. This map identifies intended relationships without claiming cell-level equivalence.

| Notebook | Primary subject | Current production counterparts | Main persisted/report outputs |
|---|---|---|---|
| `01_data_understanding.ipynb` | Source inspection and schema understanding | `retail_segmentation.data`, `retail_segmentation.eda` | Raw overview/profile tables |
| `02_data_cleaning_and_eda.ipynb` | Cleaning and exploratory analysis | `retail_segmentation.data`, `retail_segmentation.eda`, `retailai_engine.data_validation` | Cleaning audit, cleaned profiles, processed features |
| `03_customer_segmentation.ipynb` | RFM and customer segmentation | `retail_segmentation.analytics`, `retail_segmentation.clustering`, `retailai_engine.rfm_segmentation` | Customer segments, cluster model/scaler |
| `04_advanced_segmentation.ipynb` | DBSCAN, hierarchical clustering, anomalies, scoring | `retailai_engine.advanced`, `retail_segmentation.clustering`, `retailai_engine.cluster_service` | Advanced segments and cluster evaluation |
| `05_churn_prediction.ipynb` | Churn scoring and model comparison | `retailai_engine.churn_pipeline`, `retailai_engine.churn_explainer`, `retail_segmentation.predictive` | Churn metrics, model comparison, feature importance |
| `06_recommendation_engine.ipynb` | Customer/product recommendations | `retail_segmentation.recommendations`, `retailai_engine.recommendation_engine` | Recommendation CSV and catalog/database tables |
| `07_sales_forecasting.ipynb` | Forecast features and models | `retail_segmentation.forecasting`, `retailai_engine.forecast_engine` | Forecast CSVs and metrics |
| `08_explainable_ai.ipynb` | Feature importance and explainability | `retailai_engine.explainability`, `retail_segmentation.service` explanation output | Model explanations and feature-importance files |

## Traceability limitations

- Notebook output cells can be stale relative to current modules.
- Processed CSVs use older title-case field names while the current application database uses canonical snake-case names.
- No notebook metadata records the source commit, data hash, dependency lock, artifact hash, or run ID.
- Some notebook experiments may use methodology that was later corrected in production code.
- Generated files are not currently linked to exact notebook cells or pipeline commands.

## Required experiment header

Every research notebook should begin with a machine-readable or clearly structured header containing:

- Experiment ID and purpose
- Repository commit
- Python and dependency versions
- Dataset source and SHA-256
- Feature cutoff, outcome window, and split definition
- Target and feature definitions
- Random seeds
- Expected output files and locations
- Known limitations

## Promotion workflow

```text
Notebook hypothesis
→ reproducible experiment
→ leakage and validity review
→ reusable module under src/
→ unit/integration tests
→ artifact and data manifest
→ documented API/UI behavior
→ deployment validation
```

Notebook code should not be copied directly into the dashboard or API when the same logic belongs in a tested reusable module.

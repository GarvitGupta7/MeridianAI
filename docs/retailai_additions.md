# RetailAI Nexus Additions

This layer is intentionally additive to MeridianAI. The existing dashboard and
existing retail_segmentation workflow remain the primary application.

## Added capabilities

- RFM-backed customer scoring remains available through the existing analytics layer.
- KMeans, DBSCAN, hierarchical clustering and Isolation Forest are available through the advanced segmentation layer.
- Dedicated churn comparison with Logistic Regression, Decision Tree, Random Forest and XGBoost.
- Accuracy, precision, recall, F1, ROC AUC and confusion matrices.
- Churn feature importance and SHAP explanations.
- Production-safe reusable customer preprocessing pipeline.
- Collaborative filtering through customer-product matrices.
- Customer similarity and product similarity.
- Popularity recommendations and cold-start fallback.
- Forecast feature engineering with lag, rolling, calendar and trend variables.
- Linear Regression, Random Forest and XGBoost forecast comparison.
- Forecast uncertainty bounds.
- Batch churn predictions.
- Optional FastAPI endpoints under `/retailai/*`.
- Automated tests for the additive modules.

## Compatibility rule

`dashboard.py` is deliberately not modified by this addition. Existing Meridian
screens and workflows therefore remain unchanged. The new functionality is
available through the Python engine and optional API endpoints and can be surfaced
in future UI iterations without changing the current deployed experience.

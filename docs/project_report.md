# Meridian — Retail Intelligence Project Report

## Objective

Turn retail transactions into actionable customer segments, risk signals, purchase forecasts, and product recommendations.

## Methodology

1. Validate the input contract and clean malformed, duplicate, zero-quantity, and invalid-date records.
2. Aggregate transaction history into recency, frequency, spend, order value, tenure, purchase rate, product diversity, and return-rate features.
3. Calculate RFM, estimated CLV, churn risk, and customer health. Personas are assigned using transparent business rules.
4. Evaluate K-Means candidates from 2–8 clusters with silhouette, Davies–Bouldin, and Calinski–Harabasz indices. DBSCAN and hierarchical clustering are benchmarked for comparison.
5. Train predictive estimators and persist the selected cluster model, scaler, predictions, database tables, and quality evidence.

## Production guidance

- Configure scheduled batch ingestion and keep a versioned input snapshot with each model run.
- Replace demo/proxy labels with labels made from a time-forward observation window (for example, no purchase in the next 90 days = churn).
- Monitor input schema, missingness, score distributions, cluster sizes, model drift, and recommendation conversion.
- Use PostgreSQL by replacing the repository connection implementation; the logical table contract remains unchanged.

## Success measures

Track incremental revenue from targeted actions, retention among at-risk customers, conversion of recommendations, CLV uplift, and silhouette/model drift on every retraining cycle.

# MeridianAI technical and research report

## 1. Project identity

| Field | Value |
|---|---|
| Project | MeridianAI |
| Domain | AI-powered retail intelligence |
| Primary interface | Streamlit |
| API | FastAPI 1.0.0 |
| Primary language | Python |
**Current status:** Integrated engineering platform and research foundation

RetailAI Nexus is a historical engine name retained in module names and interface attribution. MeridianAI is the current authoritative project name.

## 2. Problem statement

Retail transaction systems record purchases but do not automatically provide customer prioritization, behavioural segmentation, risk signals, forecasts, or defensible action recommendations. MeridianAI transforms transaction history into customer and product intelligence through a reproducible processing, modelling, serving, and visualization workflow.

The project must satisfy two standards:

1. Engineering usefulness as a deployable retail intelligence application.
2. Scientific validity as a foundation for formal research.

## 3. Objectives

- Validate and standardize transaction exports.
- Aggregate transactions into interpretable customer features.
- Segment customers with business rules and unsupervised learning.
- Estimate customer value, health, risk, and future behaviour.
- Convert analysis into campaigns, recommendations, and sales plans.
- Expose consistent outputs through Streamlit and FastAPI.
- Preserve reproducibility, leakage awareness, and honest limitations.

## 4. Current implementation

### 4.1 Data ingestion

The canonical schema requires order ID, customer ID, transaction date, quantity, and unit price. Product code, product name, and country are optional. The application accepts CSV, XLSX, XLS, and JSON and automatically maps common business-friendly column names.

Validation and cleaning address missing identifiers, invalid dates, nonnumeric quantity/price values, duplicates, malformed rows, returns, and derived revenue.

### 4.2 Customer intelligence

The pipeline produces recency, frequency, monetary value, average order value, tenure, purchase rate, return rate, product diversity, RFM signals, estimated CLV, churn risk, health score, customer tier, cluster, persona, and campaign opportunity measures.

Current persona concepts include Premium, Loyal, At-risk, New, Big spender, Bargain shopper, and Regular customers. Assignment is mutually exclusive and priority based.

### 4.3 Segmentation

K-Means candidates from 2–8 clusters are evaluated using silhouette, Davies–Bouldin, and Calinski–Harabasz measures. DBSCAN and hierarchical clustering are retained as comparison outputs. Isolation Forest produces anomaly signals.

Cluster evaluation does not by itself prove business usefulness. Stability, interpretability, population size, and downstream actionability must also be evaluated.

### 4.4 Predictive modelling

The shared feature contract contains recency, frequency, monetary value, average order value, tenure, purchase rate, return rate, and product diversity.

The customer predictive bundle provides purchase probability, proxy churn probability, next-purchase timing, and predicted 90-day spend. The dedicated churn pipeline compares Logistic Regression, Decision Tree, Random Forest, and XGBoost when available. Metrics include accuracy, precision, recall, F1, ROC-AUC, confusion matrices, and feature importance or coefficient magnitude.

Forecast comparison supports Linear Regression, Random Forest, and optional XGBoost, with future-period and uncertainty outputs.

### 4.5 Decision support

Campaign logic considers value, churn risk, health, recency, frequency, tier, persona, and predicted future spend. Outputs include priority, strategy, action, offer, channel, incentive, reason, and opportunity score.

Recommendation functionality includes popularity, customer-product recommendations, similar customers, similar products, cross-sell, upsell, and cold-start behavior.

### 4.6 Interfaces

The Streamlit workspace has two primary pages—Overview and Customers—and three grouped menus containing nine additional pages. A global Data popover manages uploads and demo restoration.

The canonical FastAPI application contains 47 operations: 45 GET and 2 POST. Swagger and OpenAPI are generated at runtime; the maintained route list is in [API_REFERENCE.md](API_REFERENCE.md).

## 5. Persistence and reproducibility

The service persists named frames through SQLAlchemy. SQLite is the default; `DATABASE_URL` supports other SQLAlchemy connections when a compatible driver is installed. Model artifacts are serialized with joblib.

A reproducible experiment or deployment release should record:

- Source-data identity and checksum
- Feature and target definitions
- Temporal cutoff and split procedure
- Code commit
- Dependency versions
- Random seed
- Training and evaluation outputs
- Artifact checksum and storage location
- Known limitations

The current repository does not yet provide a complete automated artifact manifest or release registry.

## 6. Evaluation validity

### 6.1 Known risks

- Observed churn labels may be absent.
- Proxy churn labels can be derived from current risk information.
- Feature-derived future targets can create circular prediction.
- In-sample regression metrics do not estimate future generalization.
- Severe class imbalance can make accuracy misleading.
- Random splits can leak later customer behaviour into training data.
- Suspiciously high or identical metrics can indicate leakage or an evaluation error.

### 6.2 Required research design

A defensible research experiment should:

1. Define a feature cutoff and a strictly later outcome window.
2. Use a temporal or rolling-origin train/validation/test design.
3. Prevent the same future information from appearing in features and targets.
4. Compare simple business and statistical baselines.
5. Report per-class metrics, calibration, confidence intervals, and error analysis.
6. Run ablation studies for feature groups and modelling contributions.
7. Evaluate segmentation stability and business interpretability.
8. Separate engineering demonstration metrics from research claims.
9. Publish reproducible configurations and limitations.

No research claim should be based only on the bundled demo artifacts or an in-sample metric.

## 7. Testing

The repository contains tests intended to cover:

- End-to-end pipeline behavior
- Data validation and transformations
- Segmentation and advanced ML
- Churn pipeline behavior
- Forecast pipeline and API behavior
- Recommendation API behavior
- Explainability API behavior
- API error handling

At the documented code state, `python -m pytest -q` fails during collection. Stale tests import nonexistent paths including `src.api.main`, `src.preprocessing`, and `src.forecasting`; other tests import `retail_segmentation` without configuring `src` on the Python path. A green full-suite result must not be claimed until those imports are migrated and the suite passes in the supported Python 3.11 environment.

Even after repair, tests establish implementation behavior, not scientific validity. Both layers require independent verification.

## 8. Deployment status and limitations

The Streamlit application is configured for GitHub-backed Streamlit Cloud deployment at `https://meridian-ai.streamlit.app/`. Deployment correctness requires verification of the deployed commit, dependencies, database, artifacts, secrets, and runtime logs.

The FastAPI application has no authentication or production hardening and should remain private until those controls are added.

Other limitations include a currently non-collecting test suite, missing artifact registry, missing release-to-deployment traceability, unpinned transitive dependencies, absent formal license, and incomplete dataset provenance documentation.

## 9. Immediate research and engineering priorities

1. Establish observed time-forward outcomes and freeze the evaluation protocol.
2. Add artifact/data manifests and release identifiers.
3. Run out-of-sample baselines, ablations, calibration, and error analysis.
4. Migrate stale test imports and establish a green supported-runtime suite.
5. Add API security and production observability.
6. Add scheduled ingestion, drift monitoring, and controlled retraining.
7. Record dataset provenance, licensing, and privacy constraints.
8. Keep README, API reference, architecture, changelog, and deployed behavior synchronized with each release.

## 10. Conclusion

MeridianAI already integrates data processing, customer intelligence, machine learning, decision support, persistence, API serving, visualization, and automated tests. Its engineering breadth is substantial. Its research contribution, however, must be established through time-forward observed outcomes, leakage-safe evaluation, reproducible comparisons, and limitations supported by evidence rather than by impressive-looking metrics.

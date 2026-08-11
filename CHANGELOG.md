# Changelog

All notable changes to Meridian — Retail Intelligence are documented here.

The project follows a practical chronological changelog rather than claiming formal semantic-version releases for every internal build.

---

## [Unreleased] — Current Unified Build

### Project consolidation

- Unified the existing Meridian retail workflow with the newer RetailAI Nexus capabilities.
- Preserved the original segmentation, analytics, database, forecasting, recommendation, and dashboard functionality.
- Added the newer `retailai_engine` modules as an additive ML/predictive layer.
- Consolidated the project into a single GitHub/Streamlit deployment source.

### Dashboard / UI

- Refined the Streamlit workspace navigation.
- Added five primary workspace pages:
  - Overview
  - Customers
  - Predictive Engine
  - Customer Visuals
  - Campaigns
- Grouped additional functionality into:
  - Intelligence
  - Analytics
  - Actions
  - Data
- Added/standardized the Meridian / Retail Intelligence header treatment.
- Added RetailAI Nexus attribution in the interface.
- Refined the Predictive Engine target selection UI.
- Reworked the two prediction targets into a more structured selection interface:
  - Specific customer
  - Customer profile from filters
- Added clearer customer lookup and prediction-report presentation.
- Kept detailed portfolio charts on Customer Visuals instead of overcrowding the Predictive Engine decision page.
- Improved percentage presentation where values are probabilities/risk scores.
- Preserved the existing Streamlit deployment workflow rather than introducing a separate custom deployment control.

### Customer analytics

- Continued the customer-level RFM/behavioural feature workflow.
- Standardized customer feature usage across newer ML components.
- Added/maintained:
  - Recency
  - Frequency
  - Monetary value
  - Average order value
  - Tenure
  - Purchase rate
  - Return rate
  - Product diversity
- Maintained customer health scoring.
- Maintained churn-risk scoring.
- Maintained customer lifetime-value estimation.
- Maintained customer tier assignment.
- Maintained mutually exclusive persona assignment.

### Personas

- Implemented priority-based persona assignment.
- Current persona categories include:
  - Premium customers
  - Loyal customers
  - At-risk customers
  - New customers
  - Big spenders
  - Bargain shoppers
  - Regular customers
- Persona rules use customer value, frequency, recency, tenure, AOV, product diversity, and churn-risk information.

### Churn analytics and modelling

- Added a dedicated churn model comparison pipeline.
- Added Logistic Regression.
- Added Decision Tree.
- Added Random Forest.
- Added optional XGBoost support.
- Added:
  - Accuracy
  - Precision
  - Recall
  - F1
  - ROC-AUC
  - Confusion matrices
  - Feature importance
- Added a reusable `ChurnModelResult` structure.
- Added best-model selection using ROC-AUC followed by F1.
- Added batch churn prediction output with:
  - Churn probability
  - Churn prediction
  - Churn risk band

### Churn leakage correction

- Identified that deriving a churn target directly from `churn_risk` while also allowing risk-related information into model features can create target leakage or circular prediction.
- Updated the predictive churn workflow to use a reduced churn feature set that excludes `recency_days` for the current proxy-target workflow.
- Kept `recency_days` available for other predictive tasks where it is an intended feature.
- Added explicit documentation that proxy churn labels are not causal ground truth.
- Preserved provided `churned` / `churn` labels when available.

### Predictive engine

- Added customer-level purchase prediction.
- Added churn prediction.
- Added next-purchase timing prediction.
- Added predicted 90-day spend.
- Added customer-level prediction reports.
- Added prediction metrics for purchase classification.
- Added regression error metrics for next-purchase and spending models.
- Added model bundle handling for multiple predictive models.

### Production preprocessing

- Added a reusable production feature selector.
- Added shared `DEFAULT_FEATURES`.
- Added numeric sanitisation:
  - infinite values → missing
  - missing numeric values → zero
- Added shared scaling pipeline support.
- Added a `PreprocessingContract` for validating customer feature availability.

### Campaign engine

- Continued campaign decision logic based on:
  - customer value
  - churn risk
  - health
  - recency
  - frequency
  - tier
  - persona
  - predicted future spend
- Maintained differentiated customer treatments.
- Maintained campaign priority and opportunity scoring.
- Maintained recommended action, offer, channel, and incentive outputs.
- Avoided blanket discounting where the customer is likely to return organically.

### API

- Maintained the FastAPI service alongside the Streamlit UI.
- Maintained API routing for customer and analytics functionality.
- Maintained Swagger/OpenAPI development documentation.
- Continued separating the API/backend layer from the Streamlit presentation layer.

### Testing

- Added/maintained tests for:
  - API error handling
  - churn pipeline
  - data validation
  - explainability API
  - forecast pipeline/API
  - recommendation API
  - advanced RetailAI functionality
  - segmentation API
  - data transformers

### Deployment

- Replaced the deployed project's tracked contents with the current unified local build while preserving the existing Git repository connection/history.
- Updated the GitHub repository with the unified project structure.
- Identified GitHub's 100 MB per-file limit during deployment synchronization.
- Prevented oversized generated `.pkl` model artifacts from being committed to the GitHub repository.
- Added deployment dependency requirements through `requirements.txt`.
- Avoided using `git reset --hard` or force-push operations against the existing repository.
- Streamlit Cloud deployment was connected to the updated GitHub repository.

### Dependency / packaging cleanup

- Removed the problematic project-level Poetry packaging path from the deployment repository.
- Standardized deployment around `requirements.txt`.
- Added the primary runtime dependencies required by the Streamlit dashboard, FastAPI service, ML stack, plotting stack, data processing, and spreadsheet support.

---

## Previous Meridian functionality retained

The unified build continues to contain the earlier Meridian functionality, including:

- Retail transaction ingestion
- Data cleaning
- Customer aggregation
- RFM analysis
- Customer segmentation
- Database access
- Forecasting
- Recommendations
- Customer visuals
- Data quality checks
- Model trust
- Explainability
- Sales planning
- Campaign planning
- Streamlit dashboard navigation
- FastAPI endpoints

---

## Known limitations / follow-up work

### Large model artifacts

Some generated ML artifacts are larger than GitHub's hard file-size limit.

These should be stored outside normal Git tracking if required by deployment.

### Proxy churn labels

When observed churn labels are unavailable, proxy labels are used. These should not be interpreted as verified real-world churn outcomes.

### Synthetic future targets

Some predictive outputs are currently based on feature-derived proxy targets/formulas. Production deployment should replace these with observed historical future outcomes when sufficient longitudinal data becomes available.

### Evaluation methodology

Some regression metrics in the current predictive bundle are in-sample metrics. They are useful for engineering diagnostics but should not be presented as production generalization performance.

### Continued UI work

The workspace and page layouts remain under active refinement as the unified Meridian/RetailAI interface is consolidated.

---

## Earlier project direction

The project evolved from a retail customer segmentation/analytics application into a broader retail intelligence operating system.

The progression has included:

```text
Transaction data
      ↓
Cleaning & validation
      ↓
Customer aggregation
      ↓
RFM / segmentation
      ↓
Customer health & risk
      ↓
Personas & tiers
      ↓
Predictive ML
      ↓
Campaign decisions
      ↓
Recommendations / sales planning
      ↓
Explainability / model trust
      ↓
Unified RetailAI Nexus workspace
```

---

## Documentation policy

Future changes should update this file with:

- date/build identifier when useful,
- new functionality,
- behavioural changes,
- bug fixes,
- modelling changes,
- data-contract changes,
- deployment changes,
- known limitations.

Avoid recording routine formatting-only edits unless they affect user-facing behaviour.

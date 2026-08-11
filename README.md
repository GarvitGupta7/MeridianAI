# Meridian — Retail Intelligence

**Meridian** is a retail intelligence and customer analytics platform built around the **RetailAI Nexus** engine. It turns transaction-level retail data into customer-level intelligence, segmentation, predictive signals, campaign decisions, sales-planning insights, data-quality checks, model diagnostics, recommendations, and explainability.

The current project is a unified build containing the original Meridian workflow plus the newer RetailAI/Nexus predictive and ML capabilities.

---

## 1. What Meridian Does

Meridian is designed to answer four practical questions:

1. **What is happening?**
   - Revenue and transaction performance
   - Customer portfolio size
   - RFM/customer behaviour
   - Data quality
   - Customer health and risk

2. **Which customers matter most?**
   - Customer segmentation
   - Customer tiers
   - Personas
   - High-value and at-risk customers
   - Priority actions

3. **What is likely to happen next?**
   - Purchase probability
   - Churn probability
   - Next-purchase timing
   - Predicted 90-day spend
   - Customer scoring

4. **What should the business do?**
   - Campaign strategy
   - Retention actions
   - Recommended offers/channels
   - Sales planning
   - Customer-level decision reports

---

## 2. Main Workspace

The Streamlit workspace is organized into five primary navigation areas plus grouped dropdowns:

### Main pages

- **Overview** — portfolio-level retail intelligence and operating summary.
- **Customers** — customer-level exploration and customer records.
- **Predictive Engine** — forward-looking customer predictions and decision reports.
- **Customer Visuals** — analytical/customer portfolio visualizations.
- **Campaigns** — campaign and customer-treatment decisions.

### Grouped pages

**Intelligence**
- Predictive Engine
- Model Trust
- Explainability

**Analytics**
- Customer Visuals
- Advanced ML
- Data Quality

**Actions**
- Campaigns
- Sales Planning
- Recommendations

**Data**
- Data upload / dataset controls and related data operations.

The navigation is intentionally grouped so the workspace does not become a long collection of unrelated buttons.

---

## 3. Current Predictive Capabilities

The predictive layer includes customer-level models for:

- Purchase probability
- Churn probability
- Next-purchase timing
- Predicted 90-day spend

The current predictive bundle uses customer feature snapshots including:

- `recency_days`
- `frequency`
- `monetary_value`
- `avg_order_value`
- `tenure_days`
- `purchase_rate`
- `return_rate`
- `product_diversity`

The predictive models use Random Forest classifiers/regressors for the current purchase, churn, next-purchase, and spending workflows.

### Important modelling note

Some retail datasets do not contain a real historical churn outcome. In those cases Meridian uses an explicitly labelled **proxy churn target** rather than presenting the derived label as causal ground truth.

The project therefore distinguishes between:

- provided `churned` / `churn` labels, and
- proxy labels derived from existing customer-risk information.

This distinction is important when interpreting model metrics.

---

## 4. Churn Model Comparison

The dedicated churn pipeline supports comparison of:

- Logistic Regression
- Decision Tree
- Random Forest
- XGBoost when the optional dependency is available

The comparison layer reports:

- Accuracy
- Precision
- Recall
- F1
- ROC-AUC
- Confusion matrices
- Feature importance / coefficient magnitude

The pipeline uses a shared customer feature-selection contract and separates preprocessing from model execution.

---

## 5. Customer Analytics

The analytics layer currently includes customer-level calculations for:

- Recency
- Frequency
- Monetary value
- Average order value
- Tenure
- Purchase rate
- Return rate
- Product diversity
- Churn risk
- Customer health
- Customer lifetime value estimates
- Customer personas
- Customer tiers
- Campaign opportunity scores

Personas are mutually exclusive and priority-based. Current persona concepts include:

- Premium customers
- Loyal customers
- At-risk customers
- New customers
- Big spenders
- Bargain shoppers
- Regular customers

---

## 6. Campaign Decision Engine

The campaign engine converts customer intelligence into differentiated actions rather than applying one generic treatment to an entire risk group.

Decision inputs include:

- Customer value
- Churn risk
- Health score
- Recency
- Frequency
- Customer tier
- Persona
- Predicted future spend

Outputs can include:

- Priority
- Campaign strategy
- Recommended action
- Suggested offer
- Recommended channel
- Incentive level
- Campaign reason
- Campaign opportunity score

The intent is to protect high-value customers while avoiding unnecessary discounting for customers who are likely to return or grow organically.

---

## 7. Data

The original retail workflow works from transaction-level retail data. A representative source schema is:

```text
Invoice
StockCode
Description
Quantity
InvoiceDate
Price
Customer ID
Country
```

The platform transforms transaction-level records into customer-level features used throughout the intelligence and predictive layers.

### Data processing principles

- Missing values are handled explicitly.
- Infinite numeric values are sanitized.
- Customer features are converted to numeric form before ML processing.
- Shared feature contracts are used by production ML modules.
- Dataset state is preserved while navigating the Streamlit workspace.

---

## 8. Architecture

The project is organized as a layered retail intelligence application.

```text
                    ┌─────────────────────────┐
                    │      Streamlit UI        │
                    │       dashboard.py      │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │   Retail Intelligence   │
                    │     Application Layer   │
                    └────────────┬────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
          ▼                      ▼                      ▼
   Segmentation            Predictive ML          Decision Engines
   & Analytics             & Churn Models        & Recommendations
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 ▼
                    ┌─────────────────────────┐
                    │   Data / Database       │
                    └─────────────────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    FastAPI service      │
                    │      API endpoints      │
                    └─────────────────────────┘
```

### Key directories

```text
UnifiedMeridianAI/
├── dashboard.py
├── src/
│   ├── retailai_engine/
│   │   ├── advanced.py
│   │   ├── churn_pipeline.py
│   │   ├── production_pipeline.py
│   │   ├── predictive.py
│   │   ├── explainability.py
│   │   ├── forecast_engine.py
│   │   ├── recommendation_engine.py
│   │   ├── segmentation.py
│   │   └── ...
│   └── retail_segmentation/
│       ├── analytics.py
│       ├── data.py
│       ├── database.py
│       ├── forecasting.py
│       ├── predictive.py
│       ├── recommendations.py
│       └── ...
├── dashboard/
├── database/
├── data/
├── Models/
├── Notebooks/
├── Reports/
├── Deployment/
├── artifacts/
├── tests/
├── docs/
└── requirements.txt
```

The exact contents may evolve as additional capabilities are added.

---

## 9. Production ML Feature Contract

New ML modules share a common customer feature contract:

```text
recency_days
frequency
monetary_value
avg_order_value
tenure_days
purchase_rate
return_rate
product_diversity
```

The reusable preprocessing pipeline selects the contract, replaces infinite values, handles missing values, converts features to numeric form, and can apply standard scaling where required.

This prevents each ML module from silently implementing a different preprocessing definition.

---

## 10. API

Meridian also contains a FastAPI service for programmatic access to customer and analytics functionality.

Typical development startup:

```powershell
uvicorn src.retail_segmentation.main:app --reload
```

Depending on the current API entry point/configuration, the exact module path may differ. The FastAPI service is separate from the Streamlit presentation layer.

Swagger documentation is available during local development at:

```text
http://127.0.0.1:8000/docs
```

---

## 11. Running Locally

### Create/activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Install dependencies

```powershell
pip install -r requirements.txt
```

### Start Streamlit

```powershell
streamlit run dashboard.py
```

The dashboard normally opens at:

```text
http://localhost:8501
```

### Start FastAPI separately

```powershell
uvicorn src.retail_segmentation.main:app --reload
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 12. Deployment

The Streamlit deployment uses the GitHub repository as the source of truth.

The deployment flow is:

```text
Local development
       ↓
Git commit
       ↓
GitHub repository
       ↓
Streamlit Cloud
       ↓
Install requirements.txt
       ↓
Run dashboard.py
```

The repository should contain a valid `requirements.txt` so the deployment environment can install the application's dependencies without attempting to install the repository itself as an unrelated Python package.

### Generated ML artifacts

Large generated model files such as `.pkl` artifacts should not be committed directly when they exceed GitHub's file-size limits.

If a model is required at runtime in deployment, it should be supplied through an appropriate artifact-storage/deployment mechanism or regenerated during deployment.

---

## 13. Testing

The project contains a `tests/` directory covering areas including:

- API error handling
- Churn pipeline
- Data validation
- Explainability API
- Forecast pipeline/API
- Recommendation API
- RetailAI advanced functionality
- Segmentation API
- Transformers

Run the test suite with:

```powershell
pytest
```

---

## 14. Design Principles

The current build follows several principles:

### Separate analysis from decisions

Charts and portfolio analysis belong in analytical pages. Decision pages focus on actions and predictions.

### Avoid leakage

Targets must not be constructed directly from the same information used as model features when the resulting metric would become misleading.

### Distinguish proxy targets from ground truth

A derived churn-risk label is treated as a proxy rather than a real-world observed churn outcome.

### Reuse preprocessing

Production ML modules use shared feature definitions and preprocessing contracts.

### Preserve navigation state

Dataset and analysis state should remain usable while navigating the workspace.

### Keep the UI business-oriented

Technical model outputs are translated into customer, campaign, and sales decisions rather than exposing only raw ML metrics.

---

## 15. Current Status

### Implemented

- Streamlit retail intelligence dashboard
- Unified workspace navigation
- Customer analytics
- Customer segmentation
- Customer personas
- Customer tiers
- Churn-risk analytics
- Customer health scoring
- Predictive engine
- Purchase prediction
- Churn prediction
- Next-purchase prediction
- 90-day spending prediction
- Dedicated churn model comparison
- Logistic Regression
- Decision Tree
- Random Forest
- XGBoost support
- Campaign decision engine
- Sales-planning functionality
- Recommendations
- Explainability functionality
- Data-quality functionality
- Model-trust functionality
- Customer visualizations
- FastAPI service
- API documentation through Swagger
- Automated test coverage across major ML/API components
- Streamlit deployment configuration
- GitHub-based deployment workflow
- Shared production preprocessing contract
- Leakage reduction for churn modelling
- Customer-level decision reporting

### In progress / operational considerations

- Production artifact storage for large ML models
- Further deployment hardening
- Continued UI refinement
- Additional real-world labelled outcomes for supervised predictive models

---

## 16. Limitations

Meridian is an engineering/project implementation and not a guarantee of future customer behaviour.

Particular care is required when:

- the dataset has no observed churn labels,
- proxy targets are used,
- future-outcome labels are synthetically constructed,
- predictions are evaluated in-sample,
- transaction history is too short,
- customer identities or timestamps are incomplete.

Model metrics should therefore be interpreted in the context of the target definition and evaluation methodology.

---

## 17. Project Identity

**Project:** Meridian — Retail Intelligence  
**Engine:** RetailAI Nexus  
**Primary interface:** Streamlit  
**API layer:** FastAPI  
**Primary language:** Python  
**Focus:** Retail analytics, customer intelligence, predictive ML, segmentation, recommendations, and decision support.

---

## 18. License / Usage

This repository is intended as an academic/project implementation unless a separate license or usage agreement is provided.

Do not commit credentials, private customer information, API keys, passwords, or other secrets to the repository.

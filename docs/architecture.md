# Architecture

```mermaid
flowchart LR
    A[Retail CSV / Database] --> B[Validation & Cleaning]
    B --> C[Feature Engineering]
    C --> D[RFM · CLV · Health · Churn]
    D --> E[Clustering: K-Means / DBSCAN / Hierarchical]
    E --> F[Personas & Predictive Models]
    B --> G[Recommendation Engine]
    F --> H[(SQLite / PostgreSQL adapter)]
    G --> H
    H --> I[FastAPI REST API]
    H --> J[Streamlit + Plotly Dashboard]
```

## Components

| Layer | Responsibility |
|---|---|
| Data engineering | Canonicalizes source fields, validates schema, removes malformed/duplicate rows, calculates revenue and return flags. |
| Analytics | Builds RFM scores, proxy CLV, explainable churn risk, health score, and exclusive customer personas. |
| Machine learning | Robust-scaled K-Means selection by silhouette score; DBSCAN and hierarchical results retained as governance benchmarks. |
| Predictive | Random forest purchase, churn, next-purchase and 90-day-spend models. The bundled demo uses transparent proxy labels; replace them with time-forward outcomes in production. |
| Serving | SQLite tables plus persisted model artifacts, exposed through FastAPI and Streamlit. |


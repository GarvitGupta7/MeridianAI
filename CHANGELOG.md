# Changelog

Notable MeridianAI changes are recorded here. The repository does not yet publish formal semantic-version releases; dated entries identify documentation and implementation states without inventing release numbers.

## Unreleased

### Documentation

- Use MeridianAI as the authoritative current product name.
- Correct the Streamlit navigation to two primary pages, three grouped menus, and the Data popover.
- Replace the obsolete `UnifiedMeridianAI` tree and nonexistent directories/modules with the current repository structure.
- Document the canonical FastAPI launcher and explicitly distinguish the command-line `main.py` module.
- Add a maintained reference for all 47 FastAPI operations.
- Add environment, database, persistence, security, artifact, and deployment guidance.
- Rewrite the architecture around the shared service/repository used independently by Streamlit and FastAPI.
- Expand the technical report with current implementation and research-validity requirements.
- Reclassify the RetailAI Nexus document as a historical integration note and remove the obsolete `/retailai/*` claim.
- Clarify that no formal license is currently included.
- Record the current test-collection failure and stale import paths instead of claiming green automated coverage.
- Add data-governance documentation with a raw dataset fingerprint, probable UCI Online Retail II identification, citation, privacy classification, and manifest requirements.
- Add a dictionary for all 18 tables in the bundled application database.
- Add a model/artifact card with SHA-256 fingerprints, committed metric context, and promotion criteria.
- Add notebook-to-production traceability and a leakage-safe research evaluation protocol.
- Add deployment, backup, rollback, monitoring, incident, and release procedures.
- Add standard security and contribution policies.
- Document the current lack of explicit API response models and add representative response shapes.
- Add a credential-free `.env.example` for the optional `DATABASE_URL` setting.
- Add a confirmed future-work roadmap covering software licensing, verified deployment records, secured production FastAPI deployment, leakage-safe research evaluation, model-training provenance, and complete test-suite repair.

## 2026-08-13 — Canonical unified build

### API wiring

- Establish `src.retail_segmentation.api:app` as the canonical FastAPI application.
- Include `src.api.retailai.router` in that application without a URL prefix.
- Provide `python -m src.api.run` as the development launcher.
- Maintain generated Swagger UI and OpenAPI documentation.
- Expose 47 operations: 45 GET and 2 POST.

### Dashboard and navigation

- Consolidate the Streamlit workspace around two primary pages: Overview and Customers.
- Group Predictive Engine, Model Trust, and Advanced ML under Intelligence.
- Group Customer Visuals and Data Quality under Analytics.
- Group Campaigns, Sales Planning, Recommendations, and Explainability under Actions.
- Add a global Data popover for upload, field mapping, analysis, and demo restoration.
- Preserve uploaded analysis in session state while navigating.
- Keep portfolio visual investigation separate from customer-level predictive decision reports.

### Customer intelligence

- Maintain RFM, value, health, churn-risk, tier, persona, and campaign-opportunity measures.
- Use mutually exclusive, priority-based personas.
- Maintain high-value, high-risk, campaign, cohort, and customer-report outputs.

### Modelling

- Provide purchase, proxy-churn, next-purchase, and 90-day-spend outputs.
- Compare Logistic Regression, Decision Tree, Random Forest, and optional XGBoost for churn.
- Provide advanced segmentation, anomaly detection, forecast comparison, forecast uncertainty, and recommendation methods.
- Reuse a shared customer feature and preprocessing contract.
- Preserve explicit caveats for proxy targets, feature-derived outcomes, leakage, and in-sample metrics.

### Data and persistence

- Accept CSV, XLSX, XLS, and JSON through the application upload path.
- Automatically map common transaction field names.
- Persist pipeline frames through SQLAlchemy using SQLite by default and `DATABASE_URL` as an override.
- Bundle demonstration database and model artifacts for local/deployed application behavior.

### Tests

- Add test modules intended to cover pipeline behavior, validation, transformations, churn, forecasting, recommendations, explainability, advanced ML, segmentation, and API error handling.
- Known current issue: the full suite does not collect because several tests reference package paths that are absent from the unified repository.

### Deployment

- Use `requirements.txt` for Streamlit Cloud dependency installation.
- Configure Streamlit theme and upload size under `.streamlit/config.toml`.
- Keep credentials and `.streamlit/secrets.toml` outside version control.
- Deploy the Streamlit entry point from `dashboard.py`.

## Historical evolution

MeridianAI evolved from a customer-segmentation and analytics workflow into a broader retail intelligence platform. RetailAI Nexus was the historical name of the additive advanced engine before integration. Existing `retailai_engine` and `src/api/retailai.py` identifiers remain for technical compatibility; they do not represent a separate current product.

## Documentation policy

Every material change should update the relevant documentation in the same commit:

- User-facing behavior or navigation → `README.md`
- API method, path, input, or response behavior → `docs/API_REFERENCE.md`
- Runtime, environment, database, or deployment behavior → `docs/CONFIGURATION.md`
- Component boundary or data flow → `docs/architecture.md`
- Target, feature, methodology, evaluation, or limitation → `docs/project_report.md`
- Data source, privacy, license, or schema → `docs/DATA_GOVERNANCE.md` and `docs/DATABASE_DICTIONARY.md`
- Artifact, model, metric, or promotion status → `docs/MODEL_CARD.md`
- Research experiment design → `docs/RESEARCH_EVALUATION_PLAN.md`
- Deployment or recovery process → `docs/DEPLOYMENT_RUNBOOK.md`
- Confirmed future commitment or completion criteria → `docs/ROADMAP.md`
- Notable implementation or documentation change → `CHANGELOG.md`

Documentation must describe the code that exists, distinguish planned work from implemented work, and avoid claims unsupported by evaluation evidence.

# Contributing to MeridianAI

## Scope

Contributions should improve MeridianAI without weakening reproducibility, scientific validity, data protection, or existing functionality. MeridianAI is the current product name; use RetailAI Nexus only for historical context or existing technical identifiers.

## Development workflow

1. Create a focused branch from the intended base commit.
2. Create and activate a Python 3.11 virtual environment.
3. Install `requirements.txt`.
4. Inspect the existing implementation and relevant tests before editing.
5. Keep changes scoped and avoid duplicating routes, modules, notebooks, or artifacts.
6. Run relevant checks and record failures honestly.
7. Update documentation in the same change.
8. Review the diff for data, credentials, generated files, and accidental artifacts.

## Commands

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
pytest
streamlit run dashboard.py
python -m src.api.run
```

The current test suite contains stale imports and does not fully collect. A contribution that repairs tests should preserve intended coverage and document the supported import/package layout.

## Code standards

- Preserve the layered service/repository architecture.
- Keep `src.retail_segmentation.api:app` as the canonical FastAPI application unless an intentional migration updates every caller and document.
- Avoid duplicate router registration and duplicate endpoint method/path pairs.
- Keep the transaction and customer feature contracts explicit.
- Make randomness reproducible where applicable.
- Handle missing, infinite, malformed, and out-of-range values deliberately.
- Do not deserialize untrusted joblib or pickle artifacts.
- Add or update tests for behavioral changes.

## ML and research standards

- Define the target and observation window explicitly.
- Prevent target, temporal, customer, and preprocessing leakage.
- Prefer temporal evaluation for future-behavior tasks.
- Compare appropriate simple baselines.
- Report imbalance-aware metrics, uncertainty, and limitations.
- Investigate suspiciously high, identical, or unstable results.
- Never manufacture or selectively omit results to make performance look stronger.
- Separate demonstration metrics from defensible research findings.

## Documentation requirements

Update the relevant files:

- User behavior and setup: `README.md`
- API routes: `docs/API_REFERENCE.md`
- Runtime/configuration: `docs/CONFIGURATION.md`
- Architecture: `docs/architecture.md`
- Data: `docs/DATA_GOVERNANCE.md` and `docs/DATABASE_DICTIONARY.md`
- Models and artifacts: `docs/MODEL_CARD.md`
- Research methodology: `docs/RESEARCH_EVALUATION_PLAN.md`
- Deployment: `docs/DEPLOYMENT_RUNBOOK.md`
- Notable change: `CHANGELOG.md`

## Pull-request checklist

- [ ] Change is scoped and existing behavior was inspected first.
- [ ] No credentials, private data, or unauthorized datasets are included.
- [ ] Relevant tests were run and results are reported.
- [ ] ML target and evaluation changes were reviewed for leakage.
- [ ] API and database compatibility were considered.
- [ ] Documentation and changelog are updated.
- [ ] Generated artifacts are intentional, versioned, and described.
- [ ] Deployment and rollback impact is understood.

## Licensing

The repository currently has no formal software license. Contribution and redistribution terms must be established by the repository owner before accepting third-party contributions or presenting the project as open source.

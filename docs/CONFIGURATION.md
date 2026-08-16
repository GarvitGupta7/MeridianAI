# MeridianAI configuration and operations

## Supported runtime

- Configured development version: Python 3.11
- Dependency source: `requirements.txt`
- Streamlit entry point: `dashboard.py`
- FastAPI entry point: `src.retail_segmentation.api:app`
- Command-line pipeline: `src.retail_segmentation.main`

Install dependencies in an isolated environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Environment variables

| Variable | Required | Default | Purpose |
|---|---:|---|---|
| `DATABASE_URL` | No | SQLite URL for `artifacts/retail_segmentation.db` | Override the SQLAlchemy database connection |

No other environment variables are read by the current application code. `.env` files are ignored, but the application does not automatically load them. Set `DATABASE_URL` in the process environment or add an explicit environment-loading mechanism before relying on a `.env` file.

`.env.example` records the supported variable without containing a credential. Copying it to `.env` is not sufficient by itself because no dotenv loader is currently configured.

SQLite requires no additional driver. PostgreSQL requires an installed SQLAlchemy-compatible driver, which is not currently included in `requirements.txt`.

Example for the current PowerShell session:

```powershell
$env:DATABASE_URL = "postgresql+psycopg://user:password@host:5432/meridianai"
python -m src.api.run
```

Do not commit connection strings or credentials.

## Application settings

`src/retail_segmentation/config.py` defines:

| Setting | Current value |
|---|---:|
| Random state | 42 |
| Minimum K-Means candidates | 2 |
| Maximum K-Means candidates | 8 |
| Artifact directory | `<repository>/artifacts` |
| Default database | `<repository>/artifacts/retail_segmentation.db` |

The artifact-directory property creates the directory if it does not exist.

## Streamlit settings

`.streamlit/config.toml` configures a light MeridianAI theme and a 200 MB maximum upload size. The dashboard accepts CSV, XLSX, XLS, and JSON.

`.streamlit/secrets.toml` is ignored. Use it only for Streamlit-managed secrets and never commit it.

## Persistence behavior

The pipeline service defaults to `persist=True` and replaces the named SQL tables for each completed run. `POST /analyze` uses this persistent behavior.

The Streamlit upload workflow calls the service with `persist=False`; active uploaded results are kept in session state so they do not silently replace the bundled database while the user explores the UI.

Bundled persisted files include a SQLite database and joblib model artifacts. Their compatibility depends on:

- Python and library versions
- Serialized class/module paths
- The feature contract
- The training data state
- The source code that created them

Production releases should record these values in an artifact manifest and store large artifacts in a versioned external registry.

## Development commands

```powershell
# Streamlit
streamlit run dashboard.py

# FastAPI
python -m src.api.run

# Equivalent FastAPI command
uvicorn src.retail_segmentation.api:app --reload

# Demo pipeline
python -m src.retail_segmentation.main --demo

# CSV pipeline
python -m src.retail_segmentation.main --input path\to\transactions.csv

# Tests
pytest
```

## Production checklist

Before deploying:

1. Pin or lock tested dependency versions for the release.
2. Run the full test suite.
3. Verify the active database and model artifacts.
4. Verify the exact deployed commit.
5. Keep secrets outside the repository.
6. Add authentication and authorization before exposing FastAPI publicly.
7. Add request limits, audit logging, rate limiting, HTTPS termination, and monitoring.
8. Back up persistent data and define recovery procedures.
9. Verify Streamlit upload, demo reset, navigation, downloads, and model loading.
10. Verify `/health`, `/docs`, representative endpoints, and expected failure responses.

## Known configuration gaps

- Dependencies use version ranges rather than a release lock file.
- PostgreSQL support requires a separately installed driver.
- No model registry or artifact version manifest exists.
- No API authentication configuration exists.
- No automated migration system exists; pipeline writes replace named tables.
- The deployed application URL is documented, but deployment-to-commit traceability is not automated.
- The full test suite currently fails collection because multiple tests reference removed package paths and some assume `src` is already on `PYTHONPATH`.

# Deployment and recovery runbook

## Scope

This runbook covers the current GitHub-backed Streamlit deployment and a future separately deployed FastAPI service. It records safe procedures; it does not claim that every production control is already implemented.

## Current entry points

| Component | Entry point | Local port |
|---|---|---:|
| Streamlit | `streamlit run dashboard.py` | 8501 |
| FastAPI | `python -m src.api.run` | 8000 |
| FastAPI application | `src.retail_segmentation.api:app` | — |

Deployed Streamlit URL: `https://meridian-ai.streamlit.app/`

No production FastAPI URL is documented because none is confirmed by the repository.

## Pre-deployment record

Record before every release:

- Release identifier
- Git commit and branch
- Operator and timestamp
- Python/dependency versions
- Dataset/database and artifact SHA-256 values
- Test results and accepted failures
- Configuration/secrets inventory without secret values
- Backup location and restoration check
- Previous known-good commit

## Pre-deployment validation

1. Confirm the intended diff and ensure no credentials or private data are staged.
2. Validate documentation links and the API route inventory.
3. Run the supported-runtime test suite. The current stale test imports must be repaired before a green release gate can exist.
4. Run Streamlit locally.
5. Test demo restore, upload/mapping, analysis, all navigation groups, predictions, campaigns, recommendations, charts, and downloads.
6. Run FastAPI locally and verify `/health`, `/docs`, `/openapi.json`, upload, customer, analytics, churn, forecast, and recommendation routes.
7. Confirm artifacts deserialize in the release environment.
8. Confirm database tables and record counts are expected.
9. Confirm dataset and artifact licenses/authority.
10. Back up persistent data and record the rollback commit.

## Streamlit deployment

The current flow is:

```text
Validated local state
→ intentional Git commit
→ push to GitHub main
→ Streamlit Cloud build
→ dependency installation from requirements.txt
→ dashboard.py startup
→ post-deployment verification
```

After deployment:

1. Open the deployed URL in a clean session.
2. Record the observed deployment/build commit when available.
3. Confirm the app loads without artifact warnings or exceptions.
4. Exercise the Data popover and secure demo restore.
5. Open every workspace page.
6. Run one representative prediction and recommendation.
7. Confirm downloadable outputs.
8. Review platform logs for import, memory, serialization, database, and timeout errors.

## FastAPI deployment requirements

Do not deploy FastAPI publicly in its current unauthenticated form. Before deployment add:

- Authentication and authorization
- HTTPS and trusted proxy/origin configuration
- Request and upload size limits
- Rate limiting and timeouts
- Structured logs, metrics, health/readiness checks, and alerting
- Managed database credentials and least-privilege access
- Controlled model/artifact storage
- Backup, migration, and restoration process

## Rollback

Rollback means deploying the previously recorded known-good commit together with its compatible database schema, configuration, dependency set, and artifacts. Reverting code alone may fail when serialized models or database tables changed.

Procedure:

1. Stop or isolate the unhealthy release if data corruption or security exposure is possible.
2. Preserve logs and identify the failed release commit.
3. Restore the previous release configuration and compatible artifacts.
4. Restore the database backup if the failed release performed incompatible writes.
5. Redeploy the known-good commit through the normal deployment mechanism.
6. Repeat health and functional checks.
7. Record the incident, impact, root cause, and corrective action.

Do not rewrite Git history or force-push as a rollback mechanism.

## Backup and restoration

The bundled SQLite file can be copied only while writes are controlled and consistency is assured. Production databases should use provider-native snapshots and tested point-in-time recovery where available.

Back up:

- Database
- Model and preprocessing artifacts
- Data and artifact manifests
- Release configuration
- Required reports and audit records

A backup is not considered valid until restoration has been tested in an isolated environment.

## Monitoring

Minimum signals:

- Application availability and latency
- HTTP status and error rates
- Upload and analysis failures
- Database connectivity and query errors
- Artifact loading failures
- Memory, CPU, disk, and startup duration
- Input schema, missingness, volume, and date drift
- Prediction distribution, calibration, performance, and segment drift when outcomes become available
- Campaign/recommendation outcomes and harmful-action review

## Incident priorities

| Severity | Example | Immediate action |
|---|---|---|
| Critical | Credential exposure, private-data exposure, corrupted production writes | Isolate service, revoke credentials, preserve evidence, begin incident response |
| High | App unavailable, artifacts fail to load, persistent analysis failure | Roll back or restore known-good release |
| Medium | One route/page fails, incorrect noncritical visualization | Disable affected feature or schedule urgent fix |
| Low | Documentation or cosmetic mismatch | Correct through normal reviewed change |

## Current operational gaps

- Deployed commit is not automatically recorded in the repository.
- No production FastAPI deployment is confirmed.
- No formal monitoring, alerting, backup, or incident-response integration is committed.
- No database migration tooling exists.
- No artifact registry or automated compatibility check exists.
- Full automated tests are not currently collectible.

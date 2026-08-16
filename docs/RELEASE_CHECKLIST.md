# Release checklist

## Identification

- [ ] Release/build identifier assigned
- [ ] Intended Git commit recorded
- [ ] Previous known-good commit recorded
- [ ] Release owner and timestamp recorded
- [ ] User-visible changes summarized in `CHANGELOG.md`

## Code and tests

- [ ] Diff contains only intended changes
- [ ] No duplicate API route method/path pairs
- [ ] Full supported-runtime test suite passes
- [ ] Current stale test imports are repaired or explicitly accepted as a release blocker
- [ ] Streamlit starts and all eleven pages open
- [ ] FastAPI starts through `python -m src.api.run`
- [ ] OpenAPI operation count matches `docs/API_REFERENCE.md`

## Data and models

- [ ] Dataset source, authority/license, hash, schema, and date range recorded
- [ ] Feature and target contracts recorded
- [ ] Temporal split and outcome windows recorded for research models
- [ ] Artifact hashes and compatible code/dependencies recorded
- [ ] Suspicious/perfect metrics investigated
- [ ] Model limitations and intended use reviewed
- [ ] No private or unauthorized data included

## Security and configuration

- [ ] No credentials or secrets in Git, artifacts, notebooks, logs, or screenshots
- [ ] Environment variables documented
- [ ] Database access uses least privilege
- [ ] Public APIs have authentication, authorization, HTTPS, limits, and monitoring
- [ ] Uploaded-file risks reviewed
- [ ] Only trusted joblib/pickle artifacts are loaded

## Documentation

- [ ] README matches navigation and implemented features
- [ ] API methods, paths, parameters, and examples are current
- [ ] Architecture and database dictionary are current
- [ ] Configuration and deployment runbook are current
- [ ] Data governance, model card, and research protocol are current
- [ ] Notebook-to-production mappings are current
- [ ] Broken relative links check passes

## Deployment and rollback

- [ ] Database and artifacts backed up
- [ ] Restoration or rollback path verified
- [ ] Dependencies install in the target environment
- [ ] Deployment uses the intended commit
- [ ] Post-deployment functional checks pass
- [ ] Logs show no startup, artifact, database, or import errors
- [ ] Deployed commit and verification result recorded

## Approval

- [ ] Engineering approval
- [ ] Data/research-methodology approval when models or results change
- [ ] Security/privacy approval for real data or public exposure
- [ ] Final release decision and accepted limitations recorded

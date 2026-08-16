# MeridianAI roadmap

This roadmap records confirmed future work. Items listed here are planned commitments, not claims about the current implementation.

## Priority commitments

### 1. Select and add a software license

**Current state:** No formal software license is included.

**Future work:** The repository owner will select an appropriate license after considering academic use, publication plans, third-party dependencies, dataset rights, commercial reuse, and contribution policy.

**Completion criteria:**

- A reviewed `LICENSE` file exists.
- README and contribution terms identify the selected license.
- Dataset and third-party licenses remain separately attributed.

### 2. Record and verify deployed releases

**Current state:** The Streamlit URL is known, but the repository does not maintain a verified deployment-to-commit record or deployment-health history.

**Future work:** Introduce a repeatable release record containing the deployed Git commit, build timestamp, environment, artifact identifiers, validation result, and rollback commit.

**Completion criteria:**

- Every deployment is tied to an exact Git commit.
- Post-deployment checks and health status are recorded.
- The previous known-good release and rollback procedure are verified.

### 3. Deploy and secure the production FastAPI service

**Current state:** FastAPI is implemented for local/development use, but no production API URL or authentication system is confirmed.

**Future work:** Deploy FastAPI with authentication, authorization, HTTPS, request limits, rate limiting, monitoring, audit logging, managed secrets, and least-privilege database access.

**Completion criteria:**

- A production API URL and ownership are documented.
- Authentication and role/permission behavior are tested.
- Security, availability, monitoring, backup, and incident controls pass review.
- Public API documentation matches the deployed version.

### 4. Complete leakage-safe research evaluation

**Current state:** Bundled metrics include proxy-target and in-sample results and are not sufficient for formal research conclusions.

**Future work:** Execute the protocol in `RESEARCH_EVALUATION_PLAN.md` using observed time-forward outcomes, leakage-safe splits, baselines, ablations, calibration, uncertainty analysis, robustness checks, and reproducible artifacts.

**Completion criteria:**

- Targets and future observation windows use observed outcomes.
- A final untouched temporal test set is evaluated.
- Baselines, ablations, confidence intervals, calibration, error analysis, and limitations are reported.
- Every result is reproducible from a recorded code commit, dataset manifest, configuration, and artifact manifest.

### 5. Add complete model-training provenance

**Current state:** Bundled model files have verified hashes, but their original training timestamps, training commit, dependency state, and source-data identities are incomplete.

**Future work:** Introduce a machine-readable model and data manifest for every trained artifact.

**Completion criteria:**

- Every artifact records training timestamp and code commit.
- Dataset, feature, target, split, seed, dependency, and evaluation identities are recorded.
- Artifact hashes and compatibility requirements are verified automatically.
- A model registry or versioned artifact store is used for promoted models.

### 6. Repair and pass the complete automated test suite

**Current state:** Several tests import obsolete paths such as `src.api.main`, `src.preprocessing`, and `src.forecasting`; other tests assume `src` is already on `PYTHONPATH`.

**Future work:** Migrate tests to the current package structure, establish a consistent supported-runtime test configuration, and add continuous integration.

**Completion criteria:**

- The full test suite collects without import errors.
- Tests pass under the supported Python version.
- API, pipeline, dashboard-critical services, models, data contracts, persistence, and failure paths have meaningful coverage.
- Continuous integration runs the suite for every proposed change.
- Release documentation records the exact test command and result.

## Additional production and research work

- Add dependency locking and automated vulnerability scanning.
- Introduce database migrations, integrity constraints, indexing, backups, and restoration tests.
- Add artifact registry, drift monitoring, calibration monitoring, and controlled retraining.
- Automate dataset and artifact manifests.
- Validate recommendation quality and campaign impact using appropriate offline and causal/online evaluation.
- Complete dataset provenance, privacy, retention, access, and deletion governance for real retailer data.
- Add release notes, version tags, and deployed-version traceability.

## Roadmap maintenance

When an item is completed:

1. Add implementation and evidence.
2. Update the relevant technical documentation.
3. Record the change in `CHANGELOG.md`.
4. Move the item from planned work to implemented status only after verification.

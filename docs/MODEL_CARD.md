# MeridianAI model and artifact card

## Intended use

MeridianAI models support academic exploration and retail-intelligence demonstrations involving customer segmentation, risk, purchase behavior, spending, forecasting, recommendations, and explanation.

They are not approved for autonomous consequential decisions, public scoring services, or production customer treatment without validated data, time-forward evaluation, governance, monitoring, and human oversight.

## Model families

| Capability | Current methods |
|---|---|
| Customer segmentation | K-Means; DBSCAN; hierarchical clustering |
| Anomaly detection | Isolation Forest |
| Customer predictive bundle | Random Forest classifiers/regressors |
| Churn comparison | Logistic Regression; Decision Tree; Random Forest; XGBoost when available |
| Forecast comparison | Linear Regression; Random Forest; XGBoost when available |
| Recommendations | Popularity, collaborative/similarity, cross-sell, upsell, cold-start logic |
| Explanation | Feature importance, coefficient magnitude, and explanation records |

## Shared predictive features

`recency_days`, `frequency`, `monetary_value`, `avg_order_value`, `tenure_days`, `purchase_rate`, `return_rate`, and `product_diversity`.

Churn experiments can use a reduced feature set when proxy-target construction would otherwise create direct circularity. Every reported result must identify the exact target and features used.

## Bundled artifact manifest

These fingerprints describe the committed files inspected on 2026-08-16. They do not reveal when the models were trained; training timestamps and source-data hashes are not embedded in a complete manifest.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `cluster_model.joblib` | 1,799 | `AA26E7E3D1961BEC838046E1C734392EFC87525B61E6948D2B184B56D9AB2403` |
| `cluster_scaler.joblib` | 607 | `D1659BCA3BF27AAAAAF235C0320BB83C48CF4266D1A3953B0ABB5055F80B5729` |
| `predictive_models.joblib` | 4,277,698 | `836BD475D78E6F142C593AA441A74D6B3F8257ADAF5F969CA74B17DCAB1B7589` |
| `retail_segmentation.db` | 409,600 | `650E524F02D02C76CB92DF57714F25F63D60C9293181A9E09F982E4570EFC10B` |
| `run_summary.json` | 545 | `C483AF41E4AC41E6B8217D75D3FDD84B46735918D4B8B7E04C57CD8D7C9F066D` |

Joblib artifacts must be loaded only from trusted sources. Joblib/pickle deserialization can execute code.

## Bundled run summary

The committed `run_summary.json` reports:

| Measure | Value | Interpretation restriction |
|---|---:|---|
| Input/clean rows | 1,874 / 1,874 | Describes bundled application data, not the full raw UCI file |
| Customers | 240 | Bundled demo/application snapshot |
| Orders | 749 | Bundled demo/application snapshot |
| Revenue | 438,016.66 | Currency/context not encoded in the summary |
| Average health | 66.0 | Heuristic score |
| At-risk customers | 58 | Depends on current risk/persona rules |
| Selected K-Means clusters | 2 | Current snapshot |
| Silhouette | 0.854 | Internal clustering separation only |
| Purchase accuracy | 1.0 | Suspiciously perfect; not production evidence |
| Purchase ROC-AUC | 1.0 | Suspiciously perfect; requires leakage/target audit |
| Next-purchase MAE | 1.544 | Explicitly in-sample |
| Spending MAE | 114.215 | Explicitly in-sample |

The perfect purchase metrics must be investigated for proxy construction, feature/target overlap, train/test contamination, class balance, and task difficulty. They must not appear in research claims as generalization performance.

## Additional committed reports

- `Reports/churn_pipeline_metrics.csv`: accuracy `0.8435`, ROC-AUC `0.9002`; the file does not include split, target, sample, timestamp, or artifact identity.
- `Reports/forecast_pipeline_metrics.csv`: Random Forest MAE `364530.49`, RMSE `383623.78`, R² `-0.1515`, with 10 training and 3 test periods. Negative R² indicates performance worse than the comparison mean baseline on that test.
- `Reports/model_comparison.csv`: ranks four churn classifiers, with Logistic Regression first in that file. The file does not establish a reproducible experiment by itself.

These are engineering outputs, not independently verified research results.

## Training and provenance gaps

The current artifacts do not provide a complete record of:

- Training timestamp
- Training command or notebook cell
- Source-data hash and preprocessing version
- Code commit that trained each artifact
- Package versions used for serialization
- Exact feature and target definitions per model
- Train/validation/test membership or temporal cutoffs
- Random seed per artifact
- Calibration and threshold selection
- Fairness, stability, drift, or subgroup evaluation

## Limitations and risks

- Proxy labels may substitute for observed future outcomes.
- Feature-derived targets can make prediction circular.
- Random or in-sample evaluation can overstate performance.
- Customer behavior and currency/context are retailer and period specific.
- Recommendation quality is not validated through online or causal evaluation.
- Cluster metrics do not prove actionability or stability.
- Model outputs can reinforce historical bias or inappropriate discounting strategies.
- No production monitoring or automatic rollback exists.

## Required promotion criteria

Before any artifact is promoted beyond demonstration:

1. Create an immutable data and artifact manifest.
2. Use a leakage-safe time-forward evaluation.
3. Compare business, statistical, and ML baselines.
4. Report calibration, uncertainty, subgroup errors, and failure cases.
5. Validate business utility and harmful-treatment risks.
6. Pass the supported-runtime test suite.
7. Add model/version registry, monitoring, and rollback procedures.
8. Obtain human approval and document the intended deployment scope.

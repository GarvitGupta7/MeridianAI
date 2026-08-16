# Research evaluation plan

## Status

This document defines the evaluation required for defensible MeridianAI research. It is a protocol, not a claim that the experiments have already been completed.

## Research questions

1. Do MeridianAI customer features improve prediction of observed future purchase, churn, timing, or spend over simple baselines?
2. Are the customer segments stable, interpretable, and useful for differentiated business action?
3. Does the integrated pipeline improve reproducibility and decision usefulness without introducing leakage?
4. Which feature groups and modelling components contribute meaningful incremental value?

The final paper should narrow these into a specific contribution rather than claiming novelty from platform breadth alone.

## Leakage-safe data design

For each customer and prediction date:

```text
Feature window: history ending at cutoff T
Gap (optional): prevents boundary contamination
Outcome window: strictly after T
```

Examples:

- Purchase: at least one observed purchase during the next 30/60/90 days
- Churn: no purchase during a justified future inactivity window
- Next purchase: elapsed time from T to the next observed purchase
- Spend: observed revenue in the next 90 days

Customers without sufficient history or observable follow-up must be handled explicitly, not silently labelled.

## Splitting strategy

Primary evaluation should use rolling-origin or fixed time-forward splits. Customer-level grouping is required where multiple snapshots per customer exist. Preprocessing, feature selection, resampling, calibration, and threshold selection must be fitted only on training data.

Retain a final untouched temporal test period. Report dates, customers, transactions, class distribution, and exclusions for every split.

## Baselines

| Task | Required baselines |
|---|---|
| Purchase/churn | Majority class, recency/rule baseline, Logistic Regression |
| Spend/timing | Mean/median, last-value or historical-rate baseline, Linear Regression |
| Forecasting | Naive last-period, seasonal naive when applicable, moving average |
| Segmentation | RFM rules, fixed K-Means baseline, alternative clustering methods |
| Recommendations | Most-popular products, category/popularity baseline, random where informative |

## Metrics

### Classification

ROC-AUC, PR-AUC, precision, recall, F1, balanced accuracy, confusion matrix, Brier score, calibration curve, and threshold-specific business costs. Accuracy alone is insufficient.

### Regression and forecasting

MAE, RMSE, MAPE or sMAPE where valid, R², prediction-interval coverage, and comparison with naive baselines. Report scale and currency.

### Segmentation

Silhouette, Davies–Bouldin, Calinski–Harabasz, cluster-size distribution, bootstrap/temporal stability, persona agreement, interpretability, and downstream action outcomes.

### Recommendations

Precision@K, Recall@K, MAP/NDCG@K, catalog coverage, novelty/diversity, cold-start performance, and ultimately online or causal business evaluation.

## Ablation studies

At minimum compare:

- RFM only
- RFM plus tenure/order-value features
- Behavioral diversity and return features added
- Risk/health-derived features excluded
- Model with and without each proposed novel component

Proxy-target-derived variables must not be used as predictors of the same target.

## Uncertainty and statistical analysis

- Use bootstrap confidence intervals or repeated temporal folds where appropriate.
- Compare paired predictions on the same test observations.
- Report effect sizes and practical significance, not only p-values.
- Correct or qualify multiple comparisons.
- For forecast comparisons, use time-series-aware tests and inspect residual dependence.
- Document sample-size limitations and power where inference is claimed.

## Calibration and decision analysis

Probability models should be calibrated on validation data and assessed on test data. Select thresholds from explicit retention, contact, incentive, or false-positive/false-negative costs. Avoid converting a rank score into a probability without calibration evidence.

## Robustness and fairness

Evaluate performance across time periods, countries, customer-tenure bands, value tiers, return behavior, and data-quality conditions. Do not infer protected attributes. If real protected or demographic attributes are lawfully available for audit, restrict their use to approved fairness evaluation rather than targeting.

## Reproducibility package

Every reported table or figure should be recoverable from:

- A frozen code commit
- Dataset manifest and checksum
- Environment/lock file
- Configuration and seed
- Split manifest
- Executable training/evaluation command
- Raw metric output
- Artifact manifest
- Figure/table generation script or notebook

## Reporting rules

- Label proxy, synthetic, heuristic, in-sample, validation, and held-out results distinctly.
- Report failed and negative results when relevant.
- Do not select only the most favorable seed, split, model, or metric.
- Investigate perfect or identical results before publication.
- Separate current evidence from future work.

## Completion criteria

The research evaluation is complete only when the target, splits, baselines, metrics, ablations, uncertainty, calibration, robustness, reproducibility artifacts, limitations, and final held-out results are all documented and independently rerunnable.

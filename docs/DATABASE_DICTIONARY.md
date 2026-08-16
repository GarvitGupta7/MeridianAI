# Database dictionary

## Runtime database

MeridianAI uses SQLAlchemy through `RetailRepository`. The default database is `artifacts/retail_segmentation.db`; `DATABASE_URL` can select another SQLAlchemy database.

The bundled SQLite snapshot contains 18 tables. Row counts below describe the committed snapshot and will change after a persistent pipeline run.

## Table inventory

| Table | Bundled rows | Purpose |
|---|---:|---|
| `campaign_recommendations` | 240 | Customer-level campaign treatments |
| `catalog` | 60 | Product catalog and popularity/value summaries |
| `cleaned_column_profile` | 10 | Profile of cleaned columns |
| `cleaned_data_overview` | 5 | Cleaned-dataset summary metrics |
| `cleaning_audit` | 8 | Cleaning checks, affected records, and actions |
| `cluster_evaluation` | 9 | Clustering model/parameter evaluation |
| `cohort_retention` | 84 | Cohort activity and retention by period |
| `country_performance` | 4 | Revenue and order summaries by country |
| `customers` | 240 | Canonical customer intelligence table |
| `data_quality_comparison` | 3 | Before/after cleaning comparisons |
| `forecast_feature_importance` | 4 | Forecast feature importance |
| `model_explanations` | 24 | Model/feature importance records |
| `monthly_revenue` | 13 | Actual monthly revenue history |
| `raw_column_profile` | 8 | Profile of raw columns |
| `raw_data_overview` | 5 | Raw-dataset summary metrics |
| `sales_forecast` | 3 | Forecast revenue by month |
| `top_products` | 15 | Product revenue and unit rankings |
| `transactions` | 1,874 | Cleaned canonical transaction records |

## Core tables

### `transactions`

| Column | Type | Meaning |
|---|---|---|
| `invoice_id` | TEXT | Order/invoice identifier |
| `customer_id` | TEXT | Customer identifier |
| `invoice_date` | DATETIME | Transaction timestamp |
| `stock_code` | TEXT | Product identifier |
| `product_name` | TEXT | Product description |
| `quantity` | BIGINT | Units; negative values can represent returns |
| `unit_price` | FLOAT | Price per unit |
| `country` | TEXT | Country label |
| `revenue` | FLOAT | Derived transaction revenue |
| `is_return` | BIGINT | Return/cancellation flag |

### `customers`

| Column | Type | Meaning |
|---|---|---|
| `customer_id` | TEXT | Customer identifier |
| `recency_days` | BIGINT | Days since last purchase at analysis cutoff |
| `frequency` | BIGINT | Purchase/order frequency |
| `monetary_value` | FLOAT | Aggregated customer spend |
| `total_items` | BIGINT | Net/total units associated with the customer |
| `first_purchase` | DATETIME | Earliest observed purchase |
| `last_purchase` | DATETIME | Latest observed purchase |
| `avg_order_value` | FLOAT | Mean revenue per order |
| `tenure_days` | BIGINT | Observed customer tenure |
| `purchase_rate` | FLOAT | Purchase frequency normalized by tenure |
| `customer_age_days` | BIGINT | Customer age at analysis cutoff |
| `return_rate` | FLOAT | Return/cancellation proportion |
| `product_diversity` | BIGINT | Distinct-product count |
| `r_score`, `f_score`, `m_score` | BIGINT | RFM component scores |
| `rfm_score` | BIGINT | Combined RFM score |
| `clv_estimate` | FLOAT | Heuristic customer lifetime value estimate |
| `churn_risk` | FLOAT | Current churn-risk score |
| `health_score` | FLOAT | Customer health score |
| `persona` | TEXT | Mutually exclusive business persona |
| `customer_intelligence_score` | FLOAT | Composite customer score |
| `customer_tier` | TEXT | Customer value tier |
| `cluster` | BIGINT | Selected cluster label |
| `cluster_name` | TEXT | Human-readable cluster name |
| `anomaly_flag` | BIGINT | Isolation/anomaly flag |
| `anomaly_score` | FLOAT | Anomaly score |
| `purchase_probability` | FLOAT | Modelled purchase probability |
| `predicted_churn_probability` | FLOAT | Modelled/proxy churn probability |
| `predicted_next_purchase_days` | FLOAT | Estimated days to next purchase |
| `predicted_90d_spend` | FLOAT | Estimated 90-day spend |

### `campaign_recommendations`

Columns: `customer_id`, `persona`, `customer_tier`, `priority`, `campaign_strategy`, `recommended_action`, `suggested_offer`, `recommended_channel`, `incentive_level`, `campaign_reason`, `campaign_opportunity_score`, `churn_risk`, `health_score`, `clv_estimate`, `predicted_90d_spend`, `recency_days`, and `frequency`.

### `cluster_evaluation`

Columns: `silhouette`, `davies_bouldin`, `calinski_harabasz`, `n_clusters`, `noise_ratio`, `method`, and `parameter`.

### `cohort_retention`

Columns: `cohort_month`, `period`, `active_customers`, and `retention_rate`.

### `sales_forecast`

Columns: `month`, `forecast_revenue`, and `method`.

## Supporting tables

- `catalog`: `product_id`, `product_name`, `price`, `popularity`, `revenue`
- `cleaned_column_profile` and `raw_column_profile`: column name, type, missingness, uniqueness, example, range, and IQR outliers
- `cleaned_data_overview` and `raw_data_overview`: `metric`, `value`
- `cleaning_audit`: `check`, `records_affected`, `action`
- `country_performance`: `country`, `revenue`, `orders`
- `data_quality_comparison`: `metric`, `before_cleaning`, `after_cleaning`, `change`
- `forecast_feature_importance`: `feature`, `importance`
- `model_explanations`: `model`, `feature`, `importance`
- `monthly_revenue`: `month`, `revenue`
- `top_products`: `product`, `revenue`, `units`

## Integrity and migration limitations

- Frames are written with `if_exists="replace"`; the project has no migration framework.
- Pandas/SQLAlchemy persistence does not declare primary keys, foreign keys, uniqueness constraints, indexes, or check constraints in this repository layer.
- API and UI code therefore rely on logical naming and application behavior rather than database-enforced integrity.
- `customers/{customer_id}` currently searches only the first 1,000 customer rows returned by the base API helper.
- Production work should introduce explicit schema migrations, keys, indexes, constraints, backup policy, and retention controls.

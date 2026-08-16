# Data governance and provenance

## Repository dataset inventory

The repository currently includes:

| Location | Purpose | Governance status |
|---|---|---|
| `data/raw/online_retail_II.csv` | Raw historical transaction dataset | Public-dataset candidate; source attribution should be confirmed by the owner |
| `data/processed/*.csv` | Legacy/analysis outputs using the historical `CustomerID` schema | Generated outputs; generation commit and notebook/module should be recorded |
| `artifacts/retail_segmentation.db` | Current bundled demonstration database using canonical snake-case fields | Generated application state |
| `database/retailai.db` | Additional/legacy database artifact | Ownership and current runtime role should be confirmed before release |
| `Reports/*.csv` | Generated model and forecast metrics | Engineering evidence; evaluation design must accompany research use |

## Raw dataset fingerprint

Confirmed repository facts for `data/raw/online_retail_II.csv`:

| Property | Value |
|---|---|
| Rows | 1,067,371 |
| File size | 95,917,576 bytes |
| Date range | 2009-12-01 07:45:00 to 2011-12-09 12:50:00 |
| SHA-256 | `C161F3E453E8F6D6EA864258742F472C21CB53400C0BAC8DA2D09985AB56F98E` |
| Columns | Invoice, StockCode, Description, Quantity, InvoiceDate, Price, Customer ID, Country |

These characteristics match the UCI Machine Learning Repository's **Online Retail II** dataset, which contains 1,067,371 transactions from a UK non-store retailer over the same two-year period. UCI identifies Daqing Chen as creator, provides DOI [`10.24432/C5CG6D`](https://doi.org/10.24432/C5CG6D), and currently lists the dataset under CC BY 4.0.

Because the repository does not include a source/download manifest proving how the CSV was created from the UCI workbook, this relationship should be treated as a strongly supported identification pending owner confirmation—not as a cryptographically verified source chain.

Suggested citation after confirmation:

> Chen, D. (2012). Online Retail II [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5CG6D

Attribution and license details should be rechecked at the source before redistribution.

## Canonical input contract

| Field | Required | Data expectation |
|---|---:|---|
| `invoice_id` | Yes | Nonempty order/invoice identifier |
| `customer_id` | Yes | Nonempty customer identifier |
| `invoice_date` | Yes | Parseable transaction timestamp |
| `quantity` | Yes | Numeric unit count; negative values can represent returns |
| `unit_price` | Yes | Numeric per-unit price |
| `stock_code` | No | Product identifier |
| `product_name` | No | Product description |
| `country` | No | Customer/transaction country label |

Automatic mapping supports common alternatives, but a production ingestion contract should reject ambiguous mappings and record the accepted source-to-canonical mapping.

## Data-classification policy

| Class | Examples | Required handling |
|---|---|---|
| Public | Confirmed licensed benchmark dataset | Retain source, version, checksum, citation, and license |
| Internal | Retailer transaction aggregates and nonpublic operational data | Access control, purpose limitation, retention schedule, secure storage |
| Personal/pseudonymous | Customer identifiers and customer-level histories | Legal basis, minimization, pseudonymization, restricted access, deletion process |
| Secret | Passwords, tokens, database credentials | Approved secret store only; never Git, reports, notebooks, logs, or screenshots |
| Restricted | Payment data or highly sensitive customer attributes | Do not ingest without an approved design, compliance review, and dedicated controls |

The current feature set does not require names, emails, phone numbers, addresses, payment data, or protected demographic attributes. Such fields should be excluded unless a reviewed use case explicitly requires them.

## Required dataset manifest for future runs

Each research or production run should record:

- Dataset name, owner, source URL/system, and allowed purpose
- License or processing authority
- Retrieval/export timestamp
- Immutable file or snapshot identifier and SHA-256
- Row count, schema, date range, currency, and geography
- Missingness, duplicates, cancellations/returns, and cleaning decisions
- Train/validation/test time windows
- Feature cutoff and outcome window
- Pseudonymization method and identifier-handling rules
- Retention and deletion date
- Code commit and artifact identifiers produced from the data

## Privacy and ethics

- Use only the minimum customer-level data required for the documented purpose.
- Do not infer or target sensitive traits.
- Assess whether campaign logic unfairly disadvantages customer groups.
- Provide human review for high-impact customer treatment decisions.
- Do not treat model output as certainty or as the sole basis for consequential action.
- Avoid exposing individual customer records through unauthenticated APIs.
- Define correction and deletion procedures for real customer datasets.

## Known gaps

- No machine-readable dataset manifest is committed.
- The exact conversion path from the UCI workbook to the raw CSV is not recorded.
- `database/retailai.db` is not documented as an active or legacy artifact in code configuration.
- Processed CSVs use an older schema and are not linked to exact generating commits/notebooks.
- No organizational retention, deletion, or access-control policy is implemented.

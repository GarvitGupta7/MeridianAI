"""Data engineering, validation, cleaning, and feature construction."""
from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Iterable

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = {"invoice_id", "customer_id", "invoice_date", "quantity", "unit_price"}
OPTIONAL_COLUMNS = {"stock_code", "product_name", "country"}


@dataclass
class ValidationReport:
    valid: bool
    errors: list[str]
    warnings: list[str]
    rows: int


def _coalesce_duplicate_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Collapse duplicate labels by taking the first non-null value per row."""
    if not frame.columns.duplicated().any():
        return frame
    collapsed = {}
    for column in dict.fromkeys(frame.columns):
        same = frame.loc[:, frame.columns == column]
        collapsed[column] = same.iloc[:, 0] if same.shape[1] == 1 else same.bfill(axis=1).iloc[:, 0]
    return pd.DataFrame(collapsed, index=frame.index)


def normalize_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Map common retail column names to the project's canonical schema."""
    aliases = {
        "invoiceno": "invoice_id", "invoice_no": "invoice_id", "invoice": "invoice_id", "order_id": "invoice_id", "order_no": "invoice_id",
        "customerid": "customer_id", "customer": "customer_id", "client_id": "customer_id", "buyer_id": "customer_id",
        "invoicedate": "invoice_date", "date": "invoice_date", "order_date": "invoice_date", "transaction_date": "invoice_date", "purchase_date": "invoice_date",
        "price": "unit_price", "unitprice": "unit_price", "sales_price": "unit_price", "item_price": "unit_price",
        "qty": "quantity", "units": "quantity", "items": "quantity",
        "stockcode": "stock_code", "product_id": "stock_code", "sku": "stock_code", "description": "product_name", "product": "product_name", "item_name": "product_name",
    }
    out = frame.copy()
    out.columns = [str(c).strip().lower().replace(" ", "_") for c in out.columns]
    out = out.rename(columns={col: aliases.get(col, col) for col in out.columns})

    # Different exports can contain the same business field more than once,
    # for example ``Product Name`` and ``product_name``.  Coalesce those
    # aliases before any downstream grouping/reset_index operation.
    return _coalesce_duplicate_columns(out)


def auto_map_transaction_schema(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, str], list[str]]:
    """Infer the canonical transaction schema from business-friendly column names.

    The mapper intentionally understands common synonyms used by companies rather than
    requiring users to know Meridian's internal field names.
    """
    original = frame.copy()
    original_names = list(original.columns)
    normalized = original.copy()
    normalized.columns = [str(c).strip().lower().replace(" ", "_") for c in normalized.columns]
    original_by_normalized = dict(zip(normalized.columns, original_names))

    aliases = {
        "invoice_id": [
            "invoice_id", "invoice_no", "invoiceno", "invoice", "order_id", "order_no", "orderno",
            "order_number", "transaction_id", "transaction_no", "transaction_number", "receipt_id",
            "receipt_no", "bill_id", "bill_no", "sales_order", "order_number_id",
        ],
        "customer_id": [
            "customer_id", "customerid", "customer", "customer_number", "customer_no", "client_id",
            "client_number", "client_no", "buyer_id", "buyer_number", "member_id", "member_number",
            "shopper_id", "account_id",
        ],
        "invoice_date": [
            "invoice_date", "invoicedate", "date", "order_date", "transaction_date", "purchase_date",
            "purchase_timestamp", "transaction_timestamp", "timestamp", "order_timestamp", "sale_date",
            "sales_date", "created_at", "transaction_time",
        ],
        "quantity": [
            "quantity", "qty", "units", "units_sold", "unit_sold", "items", "items_sold", "count",
            "volume", "number_of_units", "units_purchased",
        ],
        "unit_price": [
            "unit_price", "unitprice", "unit_price_each", "price", "sales_price", "selling_price",
            "item_price", "price_per_unit", "unit_cost", "rate", "item_rate",
        ],
    }

    alias_to_target = {alias: target for target, names in aliases.items() for alias in names}
    mapping: dict[str, str] = {}
    used_targets: set[str] = set()

    # Exact business-name matches first.
    for col in list(normalized.columns):
        if col in alias_to_target:
            target = alias_to_target[col]
            if target not in used_targets:
                normalized = normalized.rename(columns={col: target})
                mapping[str(original_by_normalized.get(col, col))] = target
                used_targets.add(target)

    # Fuzzy/content-aware fallback for unfamiliar company names.
    candidates = {
        "invoice_id": ["invoice", "order", "transaction", "receipt", "bill", "reference"],
        "customer_id": ["customer", "client", "buyer", "member", "shopper", "account"],
        "invoice_date": ["date", "time", "timestamp", "purchase", "order", "transaction", "sale"],
        "quantity": ["quantity", "qty", "unit", "units", "item", "count", "volume", "sold"],
        "unit_price": ["price", "selling", "sale", "amount", "rate", "cost", "value", "unit"],
    }
    missing = [x for x in REQUIRED_COLUMNS if x not in normalized.columns]
    used_columns = set(normalized.columns) & REQUIRED_COLUMNS
    for target in missing:
        best_column, best_score = None, 0.0
        for column in normalized.columns:
            if column in used_columns or column in REQUIRED_COLUMNS:
                continue
            label = str(column).lower().replace("_", " ")
            token_scores = [SequenceMatcher(None, label, word).ratio() for word in candidates[target]]
            token_hit = max(token_scores) if token_scores else 0.0
            contains = max((0.25 if word in label else 0.0) for word in candidates[target])
            score = min(1.0, token_hit + contains)
            if target in {"quantity", "unit_price"} and pd.api.types.is_numeric_dtype(normalized[column]):
                score += 0.08
            if target == "invoice_date":
                parsed = pd.to_datetime(normalized[column], errors="coerce")
                if parsed.notna().mean() >= 0.75:
                    score += 0.18
            if score > best_score:
                best_column, best_score = column, score
        if best_column is not None and best_score >= 0.78:
            normalized = normalized.rename(columns={best_column: target})
            mapping[str(best_column)] = target
            used_columns.add(target)

    normalized = _coalesce_duplicate_columns(normalized)
    return normalized, mapping, list(REQUIRED_COLUMNS - set(normalized.columns))


def validate_transactions(frame: pd.DataFrame) -> ValidationReport:
    errors: list[str] = []
    warnings: list[str] = []
    missing = REQUIRED_COLUMNS - set(frame.columns)
    if missing:
        errors.append(f"Missing required columns: {', '.join(sorted(missing))}")
    if frame.empty:
        errors.append("The transaction dataset is empty")
    if not missing:
        if frame["customer_id"].isna().mean() > 0.20:
            errors.append("More than 20% of customer IDs are missing")
        if (pd.to_numeric(frame["quantity"], errors="coerce") == 0).any():
            warnings.append("Zero-quantity rows will be discarded")
        if pd.to_datetime(frame["invoice_date"], errors="coerce").isna().any():
            warnings.append("Rows with invalid invoice dates will be discarded")
    return ValidationReport(not errors, errors, warnings, len(frame))


def clean_transactions(frame: pd.DataFrame) -> pd.DataFrame:
    """Clean retail transactions while retaining returns as useful behavior signals."""
    out = normalize_columns(frame)
    report = validate_transactions(out)
    if not report.valid:
        raise ValueError("; ".join(report.errors))
    out = out.drop_duplicates().copy()
    out["invoice_date"] = pd.to_datetime(out["invoice_date"], errors="coerce", utc=True).dt.tz_localize(None)
    out["customer_id"] = out["customer_id"].astype("string").str.strip()
    out["quantity"] = pd.to_numeric(out["quantity"], errors="coerce")
    out["unit_price"] = pd.to_numeric(out["unit_price"], errors="coerce")
    out = out.dropna(subset=["invoice_id", "customer_id", "invoice_date", "quantity", "unit_price"])
    out = out[(out["quantity"] != 0) & (out["unit_price"] >= 0)].copy()
    out["revenue"] = out["quantity"] * out["unit_price"]
    out["is_return"] = (out["quantity"] < 0).astype(int)
    for column in OPTIONAL_COLUMNS & set(out.columns):
        out[column] = out[column].astype("string").fillna("Unknown").str.strip()
    return out.sort_values("invoice_date").reset_index(drop=True)


def build_customer_features(transactions: pd.DataFrame, as_of_date: pd.Timestamp | None = None) -> pd.DataFrame:
    """Create behavior, value, product affinity, and temporal features per customer."""
    if transactions.empty:
        return pd.DataFrame(columns=["customer_id"])
    reference = pd.Timestamp(as_of_date) if as_of_date is not None else transactions["invoice_date"].max() + pd.Timedelta(days=1)
    purchases = transactions[transactions["revenue"] > 0].copy()
    if purchases.empty:
        purchases = transactions.copy()
    grouped = purchases.groupby("customer_id", observed=True)
    features = grouped.agg(
        recency_days=("invoice_date", lambda x: max(0, (reference - x.max()).days)),
        frequency=("invoice_id", "nunique"),
        monetary_value=("revenue", "sum"),
        avg_order_value=("revenue", lambda x: x.sum() / max(1, x.index.nunique())),
        total_items=("quantity", "sum"),
        first_purchase=("invoice_date", "min"),
        last_purchase=("invoice_date", "max"),
    ).reset_index()
    order_values = purchases.groupby(["customer_id", "invoice_id"], observed=True)["revenue"].sum()
    features = features.merge(order_values.groupby(level=0).mean().rename("avg_order_value").reset_index(), on="customer_id", suffixes=("_raw", ""))
    features = features.drop(columns="avg_order_value_raw")
    features["tenure_days"] = (reference - features["first_purchase"]).dt.days.clip(lower=1)
    features["purchase_rate"] = features["frequency"] / features["tenure_days"] * 30
    features["customer_age_days"] = features["tenure_days"]
    features["return_rate"] = transactions.groupby("customer_id", observed=True)["is_return"].mean().reindex(features["customer_id"]).fillna(0).to_numpy()
    if "stock_code" in purchases.columns:
        features["product_diversity"] = grouped["stock_code"].nunique().to_numpy()
    else:
        features["product_diversity"] = 0
    return features.replace([np.inf, -np.inf], 0).fillna(0)


def generate_demo_transactions(customers: int = 240, days: int = 365, seed: int = 42) -> pd.DataFrame:
    """Create a deterministic retail dataset for demos, tests, and first-run setup."""
    rng = np.random.default_rng(seed)
    start = pd.Timestamp.now().normalize() - pd.Timedelta(days=days)
    products = [(f"P{i:03d}", f"Product {i:03d}", float(rng.uniform(5, 180))) for i in range(1, 61)]
    records: list[dict] = []
    for c in range(customers):
        customer = f"C{c + 1:05d}"
        propensity = rng.gamma(1.5, 2.0)
        orders = max(1, rng.poisson(propensity))
        for order in range(orders):
            date = start + pd.Timedelta(days=int(rng.integers(0, days)))
            invoice = f"INV-{c:05d}-{order:03d}"
            for _ in range(int(rng.integers(1, 5))):
                code, name, price = products[int(rng.integers(len(products)))]
                records.append({"invoice_id": invoice, "customer_id": customer, "invoice_date": date,
                                "stock_code": code, "product_name": name, "quantity": int(rng.integers(1, 5)),
                                "unit_price": round(price * rng.uniform(0.85, 1.15), 2),
                                "country": rng.choice(["United Kingdom", "Germany", "France", "India"])})
    return pd.DataFrame(records)

"""Automated exploratory data analysis and data-quality reporting."""
from __future__ import annotations

import numpy as np
import pandas as pd


def profile_dataset(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create generic, safe EDA summaries for any tabular upload."""
    overview = pd.DataFrame([
        {"metric": "Rows", "value": len(frame)},
        {"metric": "Columns", "value": len(frame.columns)},
        {"metric": "Duplicate rows", "value": int(frame.duplicated().sum())},
        {"metric": "Missing cells", "value": int(frame.isna().sum().sum())},
        {"metric": "Memory (MB)", "value": round(float(frame.memory_usage(deep=True).sum() / 1_000_000), 2)},
    ])
    records = []
    for column in frame.columns:
        series = frame[column]
        record = {"column": str(column), "data_type": str(series.dtype), "missing_values": int(series.isna().sum()), "missing_pct": round(float(series.isna().mean() * 100), 2), "unique_values": int(series.nunique(dropna=True)), "example": str(series.dropna().iloc[0])[:80] if series.notna().any() else "—"}
        if pd.api.types.is_numeric_dtype(series):
            clean = series.dropna()
            q1, q3 = clean.quantile(.25), clean.quantile(.75)
            record.update({"min": round(float(clean.min()), 2) if len(clean) else np.nan, "max": round(float(clean.max()), 2) if len(clean) else np.nan, "outliers_iqr": int(((clean < q1 - 1.5 * (q3 - q1)) | (clean > q3 + 1.5 * (q3 - q1))).sum()) if len(clean) else 0})
        records.append(record)
    return overview, pd.DataFrame(records)


def quality_comparison(raw: pd.DataFrame, cleaned: pd.DataFrame) -> pd.DataFrame:
    return pd.DataFrame([
        {"metric": "Rows", "before_cleaning": len(raw), "after_cleaning": len(cleaned), "change": len(cleaned) - len(raw)},
        {"metric": "Duplicate rows", "before_cleaning": int(raw.duplicated().sum()), "after_cleaning": int(cleaned.duplicated().sum()), "change": int(cleaned.duplicated().sum() - raw.duplicated().sum())},
        {"metric": "Missing cells", "before_cleaning": int(raw.isna().sum().sum()), "after_cleaning": int(cleaned.isna().sum().sum()), "change": int(cleaned.isna().sum().sum() - raw.isna().sum().sum())},
    ])


def retail_eda(transactions: pd.DataFrame) -> dict[str, pd.DataFrame]:
    purchases = transactions[transactions.revenue > 0].copy()
    monthly = purchases.set_index("invoice_date").resample("MS").revenue.sum().rename("revenue").reset_index().rename(columns={"invoice_date": "month"})
    top_products = pd.DataFrame(columns=["product", "revenue", "units"])
    if "product_name" in purchases.columns:
        top_products = purchases.groupby("product_name", observed=True).agg(revenue=("revenue", "sum"), units=("quantity", "sum")).sort_values("revenue", ascending=False).head(15).reset_index().rename(columns={"product_name": "product"})
    countries = pd.DataFrame(columns=["country", "revenue", "orders"])
    if "country" in purchases.columns:
        countries = purchases.groupby("country", observed=True).agg(revenue=("revenue", "sum"), orders=("invoice_id", "nunique")).sort_values("revenue", ascending=False).head(15).reset_index()
    return {"monthly_revenue": monthly, "top_products": top_products, "country_performance": countries}


def cleaning_audit(raw: pd.DataFrame, cleaned: pd.DataFrame) -> pd.DataFrame:
    """Explain exactly what the cleaning pipeline changed in the uploaded data."""
    required = ["invoice_id", "customer_id", "invoice_date", "quantity", "unit_price"]
    rows = []
    duplicate_count = int(raw.duplicated().sum())
    missing_required = int(raw[required].isna().any(axis=1).sum()) if set(required).issubset(raw.columns) else 0
    invalid_dates = int(pd.to_datetime(raw["invoice_date"], errors="coerce").isna().sum()) if "invoice_date" in raw.columns else 0
    invalid_quantity = int(pd.to_numeric(raw["quantity"], errors="coerce").isna().sum()) if "quantity" in raw.columns else 0
    invalid_price = int(pd.to_numeric(raw["unit_price"], errors="coerce").isna().sum()) if "unit_price" in raw.columns else 0
    zero_quantity = int((pd.to_numeric(raw["quantity"], errors="coerce") == 0).sum()) if "quantity" in raw.columns else 0
    negative_price = int((pd.to_numeric(raw["unit_price"], errors="coerce") < 0).sum()) if "unit_price" in raw.columns else 0
    rows_removed = len(raw) - len(cleaned)
    actions = [
        ("Duplicate rows", duplicate_count, "Removed" if duplicate_count else "None"),
        ("Rows with missing required fields", missing_required, "Removed" if missing_required else "None"),
        ("Invalid transaction dates", invalid_dates, "Removed" if invalid_dates else "None"),
        ("Non-numeric quantities", invalid_quantity, "Removed" if invalid_quantity else "None"),
        ("Non-numeric prices", invalid_price, "Removed" if invalid_price else "None"),
        ("Zero-quantity rows", zero_quantity, "Removed" if zero_quantity else "None"),
        ("Negative-price rows", negative_price, "Removed" if negative_price else "None"),
    ]
    for issue, count, action in actions:
        rows.append({"check": issue, "records_affected": count, "action": action})
    rows.append({"check": "Total rows removed", "records_affected": max(0, rows_removed), "action": "Cleaning complete"})
    return pd.DataFrame(rows)

"""
==========================================================
Meridian

Module:
Retail Data Validation

Description:
Validates uploaded retailer transaction data, supports
common column aliases and reports clear data-quality
issues before analytics are calculated.

Author:
Garvit Gupta

Version:
2.0.0

Last Updated:
July 2026
==========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
import re

import pandas as pd


REQUIRED_TRANSACTION_COLUMNS = {
    "Invoice",
    "Description",
    "Quantity",
    "InvoiceDate",
    "Price",
    "Customer ID",
}

COLUMN_ALIASES = {
    "invoice": "Invoice",
    "invoiceno": "Invoice",
    "invoicenumber": "Invoice",
    "orderid": "Invoice",
    "ordernumber": "Invoice",
    "transactionid": "Invoice",
    "description": "Description",
    "product": "Description",
    "productname": "Description",
    "productdescription": "Description",
    "item": "Description",
    "itemdescription": "Description",
    "quantity": "Quantity",
    "qty": "Quantity",
    "units": "Quantity",
    "unitssold": "Quantity",
    "quantitysold": "Quantity",
    "invoicedate": "InvoiceDate",
    "date": "InvoiceDate",
    "transactiondate": "InvoiceDate",
    "orderdate": "InvoiceDate",
    "purchasedate": "InvoiceDate",
    "saledate": "InvoiceDate",
    "price": "Price",
    "unitprice": "Price",
    "priceeach": "Price",
    "salesprice": "Price",
    "customerid": "Customer ID",
    "customer": "Customer ID",
    "customernumber": "Customer ID",
    "clientid": "Customer ID",
    "clientnumber": "Customer ID",
    "buyerid": "Customer ID",
    "country": "Country",
    "market": "Country",
}


@dataclass
class DataValidationResult:
    """Result returned after checking a retailer transaction dataset."""

    is_valid: bool
    dataframe: pd.DataFrame
    errors: list[str]
    warnings: list[str]


def _normalise_column_name(column_name: object) -> str:
    """Make a source-system header comparable across casing and punctuation."""
    return re.sub(r"[^a-z0-9]+", "", str(column_name).strip().lower())


def standardize_transaction_columns(
    dataframe: pd.DataFrame,
) -> tuple[pd.DataFrame, list[str]]:
    """Map common retail-system headers to Meridian's canonical data contract.

    Exact Meridian headers take precedence. Ambiguous duplicate mappings are
    retained under their source name so no data is silently overwritten.
    """
    cleaned_data = dataframe.copy()
    cleaned_data.columns = [str(column).strip() for column in cleaned_data.columns]
    canonical_headers = set(REQUIRED_TRANSACTION_COLUMNS) | {"Country"}
    claimed_headers = set(cleaned_data.columns) & canonical_headers
    rename_map: dict[str, str] = {}
    mappings: list[str] = []
    warnings: list[str] = []

    for source_header in cleaned_data.columns:
        target_header = COLUMN_ALIASES.get(_normalise_column_name(source_header))
        if target_header is None or source_header == target_header:
            continue
        if target_header in claimed_headers:
            warnings.append(
                f"Ignored automatic mapping for '{source_header}' because "
                f"'{target_header}' is already present."
            )
            continue
        rename_map[source_header] = target_header
        claimed_headers.add(target_header)
        mappings.append(f"{source_header} → {target_header}")

    cleaned_data = cleaned_data.rename(columns=rename_map)
    if mappings:
        warnings.insert(0, f"Automatically mapped columns: {', '.join(mappings)}.")
    return cleaned_data, warnings


def validate_transaction_data(dataframe: pd.DataFrame) -> DataValidationResult:
    """Validate the minimum data needed for Meridian analytics.

    The function accepts common alternative column names and standardises them
    before checking the data. It does not delete rows, so the user can decide
    how to handle any quality warnings shown in the application.
    """
    if not isinstance(dataframe, pd.DataFrame):
        raise TypeError("Transaction data must be provided as a pandas DataFrame.")

    errors: list[str] = []
    cleaned_data, warnings = standardize_transaction_columns(dataframe)

    missing_columns = REQUIRED_TRANSACTION_COLUMNS - set(cleaned_data.columns)
    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))
        errors.append(f"Missing required column(s): {missing_text}.")
        return DataValidationResult(False, cleaned_data, errors, warnings)

    if cleaned_data.empty:
        errors.append("The uploaded file does not contain any rows.")

    duplicate_count = int(cleaned_data.duplicated().sum())
    if duplicate_count:
        warnings.append(f"{duplicate_count} duplicate row(s) were found.")

    invoice_dates = pd.to_datetime(
        cleaned_data["InvoiceDate"],
        errors="coerce",
    )
    if invoice_dates.isna().any():
        errors.append(
            f"{invoice_dates.isna().sum()} row(s) have an invalid InvoiceDate."
        )
    else:
        cleaned_data["InvoiceDate"] = invoice_dates

    for column_name in ["Quantity", "Price"]:
        numeric_values = pd.to_numeric(
            cleaned_data[column_name],
            errors="coerce",
        )
        if numeric_values.isna().any():
            errors.append(
                f"{numeric_values.isna().sum()} row(s) have a non-numeric "
                f"{column_name} value."
            )
        elif (numeric_values <= 0).any():
            errors.append(
                f"{(numeric_values <= 0).sum()} row(s) have a non-positive "
                f"{column_name} value."
            )
        else:
            cleaned_data[column_name] = numeric_values

    if cleaned_data["Customer ID"].isna().any():
        errors.append(
            f"{cleaned_data['Customer ID'].isna().sum()} row(s) have no customer ID."
        )

    return DataValidationResult(not errors, cleaned_data, errors, warnings)

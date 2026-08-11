"""
==========================================================
Meridian

Module:
Retail Data Validation Tests

Description:
Tests required-column checks and common source-system
column aliases for uploaded retailer transaction data.

Author:
Garvit Gupta

Version:
2.0.0

Last Updated:
July 2026
==========================================================
"""

import pandas as pd

from src.preprocessing.data_validation import validate_transaction_data


def valid_transactions() -> pd.DataFrame:
    """Return a small valid transaction dataset."""
    return pd.DataFrame(
        {
            "Invoice": ["1001"],
            "Description": ["Coffee Mug"],
            "Quantity": [2],
            "InvoiceDate": ["2026-01-01"],
            "Price": [8.5],
            "Customer ID": [101],
        }
    )


def test_valid_transaction_data_passes_validation():
    """A complete transaction dataset should be accepted."""
    result = validate_transaction_data(valid_transactions())

    assert result.is_valid
    assert result.errors == []


def test_common_column_aliases_are_standardised():
    """Common source-system headers should map to the data contract."""
    aliased_data = valid_transactions().rename(
        columns={"Customer ID": "CustomerID", "Price": "UnitPrice"}
    )
    result = validate_transaction_data(aliased_data)

    assert result.is_valid
    assert "Customer ID" in result.dataframe.columns
    assert "Price" in result.dataframe.columns


def test_messy_retail_headers_are_mapped_automatically():
    """Casing, punctuation, and common source-system names should not block uploads."""
    source_data = valid_transactions().rename(
        columns={
            "Invoice": "Order ID",
            "Description": "Product Name",
            "Quantity": "QTY",
            "InvoiceDate": "Purchase-Date",
            "Price": "Price Each",
            "Customer ID": "Customer Number",
        }
    )

    result = validate_transaction_data(source_data)

    assert result.is_valid
    assert set(["Invoice", "Description", "Quantity", "InvoiceDate", "Price", "Customer ID"]).issubset(result.dataframe.columns)
    assert "Automatically mapped columns" in result.warnings[0]


def test_canonical_header_wins_over_a_duplicate_alias():
    """Automatic mapping must not overwrite a canonical column already supplied."""
    source_data = valid_transactions().assign(**{"Order ID": ["fallback-order"]})

    result = validate_transaction_data(source_data)

    assert result.is_valid
    assert result.dataframe["Invoice"].iloc[0] == "1001"
    assert any("Ignored automatic mapping" in warning for warning in result.warnings)


def test_missing_required_column_is_reported():
    """The user should see exactly why an upload cannot be analysed."""
    result = validate_transaction_data(
        valid_transactions().drop(columns="Description")
    )

    assert not result.is_valid
    assert "Description" in result.errors[0]


def test_invalid_values_and_duplicates_are_reported():
    """Unsafe transaction values must block analytics while duplicates remain visible."""
    invalid_data = pd.concat(
        [
            valid_transactions(),
            valid_transactions().assign(Quantity=0, Price=-1, InvoiceDate="bad"),
        ],
        ignore_index=True,
    )
    invalid_data.loc[1, "Customer ID"] = None

    result = validate_transaction_data(invalid_data)

    assert not result.is_valid
    assert any("invalid InvoiceDate" in error for error in result.errors)
    assert any("non-positive Quantity" in error for error in result.errors)
    assert any("no customer ID" in error for error in result.errors)
    assert result.warnings == []

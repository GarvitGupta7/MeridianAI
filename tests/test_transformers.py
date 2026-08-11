"""Tests for reusable dataframe transformers."""

import pandas as pd
import pytest

from src.preprocessing.transformers import (
    NumericCoercionTransformer,
    RequiredColumnsTransformer,
)


def test_required_columns_transformer_selects_columns_in_order():
    dataframe = pd.DataFrame({"ignored": [1], "amount": ["2"], "count": ["3"]})

    transformed = RequiredColumnsTransformer(["count", "amount"]).fit_transform(dataframe)

    assert list(transformed.columns) == ["count", "amount"]


def test_numeric_coercion_transformer_rejects_invalid_values():
    dataframe = pd.DataFrame({"amount": ["not-a-number"]})

    with pytest.raises(ValueError):
        NumericCoercionTransformer(["amount"]).fit_transform(dataframe)

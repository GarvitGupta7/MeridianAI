import pandas as pd

from retail_segmentation.data import auto_map_transaction_schema, clean_transactions, generate_demo_transactions, validate_transactions
from retail_segmentation.service import RetailSegmentationService


def test_validation_reports_missing_schema():
    report = validate_transactions(pd.DataFrame({"customer_id": ["C1"]}))
    assert not report.valid
    assert "Missing required columns" in report.errors[0]


def test_cleaning_calculates_revenue():
    source = pd.DataFrame({"invoice_id": ["1", "1"], "customer_id": ["C1", "C1"], "invoice_date": ["2024-01-01", "2024-01-01"], "quantity": [2, 0], "unit_price": [10, 4]})
    cleaned = clean_transactions(source)
    assert len(cleaned) == 1
    assert cleaned.revenue.iloc[0] == 20


def test_auto_mapping_recognizes_common_company_columns():
    source = pd.DataFrame({"Order ID": ["1"], "Client ID": ["C1"], "Purchase Date": ["2024-01-01"], "Qty": [2], "Sales Price": [10]})
    mapped, _, missing = auto_map_transaction_schema(source)
    assert not missing
    assert {"invoice_id", "customer_id", "invoice_date", "quantity", "unit_price"}.issubset(mapped.columns)


def test_full_pipeline_with_demo_data():
    service = RetailSegmentationService()
    result = service.run(generate_demo_transactions(customers=40, days=120), persist=False)
    customers = result["customers"]
    assert {"cluster", "persona", "health_score", "clv_estimate"}.issubset(customers.columns)
    assert {"customer_tier", "customer_intelligence_score", "anomaly_flag"}.issubset(customers.columns)
    assert result["evaluation"].method.nunique() == 3
    assert {"recommended_action", "priority"}.issubset(result["campaigns"].columns)
    assert not result["retention"].empty
    assert len(result["forecast"]) == 3
    assert {"before_cleaning", "after_cleaning"}.issubset(result["quality"].columns)


def test_normalize_columns_collapses_duplicate_canonical_fields():
    import pandas as pd
    from retail_segmentation.data import normalize_columns

    frame = pd.DataFrame({
        "Product Name": ["A", None],
        "product_name": [None, "B"],
        "Qty": [1, 2],
    })
    cleaned = normalize_columns(frame)
    assert list(cleaned.columns).count("product_name") == 1
    assert cleaned["product_name"].tolist() == ["A", "B"]

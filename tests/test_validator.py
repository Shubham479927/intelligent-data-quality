import pandas as pd

from src.validation.validator import validate_dataset


def test_valid_dataset_passes():
    df = pd.DataFrame({
        "order_id": [1, 2],
        "customer_id": [101, 102],
        "order_date": ["2026-01-01", "2026-01-02"],
        "product_category": ["Electronics", "Clothing"],
        "quantity": [2, 1],
        "unit_price": [100.0, 50.0],
        "total_amount": [200.0, 50.0],
        "payment_method": ["UPI", "Cash"],
        "customer_age": [25, 30],
        "customer_email": ["a@test.com", "b@test.com"]
    })

    results = validate_dataset(df)

    assert results["schema_validation"]["status"] == "PASS"
    assert results["duplicates"]["status"] == "PASS"
    assert results["quality_score"] == 100.0


def test_invalid_payment_method_fails():
    df = pd.DataFrame({
        "order_id": [1],
        "customer_id": [101],
        "order_date": ["2026-01-01"],
        "product_category": ["Electronics"],
        "quantity": [2],
        "unit_price": [100.0],
        "total_amount": [200.0],
        "payment_method": ["Crypto"],
        "customer_age": [25],
        "customer_email": ["a@test.com"]
    })

    results = validate_dataset(df)

    payment_result = results["allowed_values_validation"]["payment_method"]

    assert payment_result["invalid_count"] == 1
    assert payment_result["status"] == "FAIL"
import pandas as pd

from src.cleaning.cleaner import clean_dataset


def test_negative_quantity_is_quarantined():
    df = pd.DataFrame({
        "order_id": [1, 2],
        "customer_id": [101, 102],
        "quantity": [2, -5],
        "unit_price": [100.0, 50.0],
        "total_amount": [200.0, -250.0],
        "customer_age": [25, 30],
        "customer_email": ["a@test.com", "b@test.com"],
        "order_date": ["2026-01-01", "2026-01-02"]
    })

    cleaned_df, quarantine_df, duplicates_removed = clean_dataset(df)

    assert len(quarantine_df) == 1
    assert len(cleaned_df) == 1
    assert duplicates_removed == 0


def test_duplicate_rows_are_removed():
    df = pd.DataFrame({
        "order_id": [1, 1],
        "customer_id": [101, 101],
        "quantity": [2, 2],
        "unit_price": [100.0, 100.0],
        "total_amount": [200.0, 200.0],
        "customer_age": [25, 25],
        "customer_email": ["a@test.com", "a@test.com"],
        "order_date": ["2026-01-01", "2026-01-01"]
    })

    cleaned_df, quarantine_df, duplicates_removed = clean_dataset(df)

    assert duplicates_removed == 1
    assert len(cleaned_df) == 1
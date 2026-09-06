import pandas as pd
from pathlib import Path
import json


def clean_dataset(df):
    """
    Clean the dataset and separate invalid records.
    """

    cleaned_df = df.copy()

    # Identify invalid records
    invalid_mask = (
        (cleaned_df["quantity"] <= 0)
        | (cleaned_df["unit_price"] <= 0)
        | (cleaned_df["customer_age"] < 18)
        | (cleaned_df["customer_age"] > 100)
        | (~cleaned_df["customer_email"].fillna("").str.match(
            r"^[\w\.-]+@[\w\.-]+\.\w+$"
        ))
    )

    # Separate invalid records
    quarantine_df = cleaned_df[invalid_mask].copy()

    # Keep only valid records
    cleaned_df = cleaned_df[~invalid_mask].copy()

    # Remove duplicates from valid data
    cleaned_df = cleaned_df.drop_duplicates()

    return cleaned_df, quarantine_df


if __name__ == "__main__":

    file_path = "data/raw/ecommerce_data.csv"

    df = pd.read_csv(file_path)

    cleaned_df, quarantine_df = clean_dataset(df)
    
        # Cleaning summary
    original_rows = len(df)
    quarantine_rows = len(quarantine_df)
    cleaned_rows = len(cleaned_df)

    duplicates_removed = (
        original_rows
        - quarantine_rows
        - cleaned_rows
    )

    retention_rate = round(
        (cleaned_rows / original_rows) * 100,
        2
    )

    print("\n===== CLEANING SUMMARY =====")

    print("Original rows:", original_rows)
    print("Invalid/quarantined rows:", quarantine_rows)
    print("Duplicates removed:", duplicates_removed)
    print("Final cleaned rows:", cleaned_rows)
    print("Data retention rate:", retention_rate, "%")
    
        # Create output directories
    processed_path = Path("data/processed")
    quarantine_path = Path("data/quarantine")

    processed_path.mkdir(parents=True, exist_ok=True)
    quarantine_path.mkdir(parents=True, exist_ok=True)

    # Save cleaned data
    cleaned_file = processed_path / "cleaned_data.csv"
    cleaned_df.to_csv(cleaned_file, index=False)

    # Save quarantined data
    quarantine_file = quarantine_path / "quarantined_data.csv"
    quarantine_df.to_csv(quarantine_file, index=False)

    print("\nCleaned data saved to:", cleaned_file)
    print("Quarantined data saved to:", quarantine_file)

    print("\n===== DATA CLEANING =====")

    print("Original rows:", len(df))
    print("Cleaned rows:", len(cleaned_df))
    print("Quarantine rows:", len(quarantine_df))

    print("\n===== QUARANTINE PREVIEW =====")

    print(quarantine_df.head())
    
        # Save cleaning report

    cleaning_report = {
        "original_rows": original_rows,
        "quarantined_rows": quarantine_rows,
        "duplicates_removed": duplicates_removed,
        "cleaned_rows": cleaned_rows,
        "retention_rate": retention_rate
    }

    report_path = Path("data/cleaning_report.json")

    with open(report_path, "w") as file:
        json.dump(cleaning_report, file, indent=4)

    print("\nCleaning report saved to:", report_path)
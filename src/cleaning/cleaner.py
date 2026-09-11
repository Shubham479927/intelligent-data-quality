import pandas as pd
from pathlib import Path
import json


def clean_dataset(df):
    """
    Generic data cleaning engine.

    Separates invalid records into quarantine and
    keeps valid records in the cleaned dataset.
    """

    cleaned_df = df.copy()

    invalid_mask = pd.Series(
        False,
        index=cleaned_df.index
    )

    # 1. Numeric validation

    numeric_columns = cleaned_df.select_dtypes(
        include=["number"]
    ).columns

    for column in numeric_columns:

        column_lower = column.lower()

        # Ignore ID/code columns
        if any(
            keyword in column_lower
            for keyword in ["id", "code", "zip", "postal"]
        ):
            continue

        invalid_mask |= cleaned_df[column] < 0

    # 2. Email validation

    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    for column in cleaned_df.columns:

        if "email" in column.lower():

            non_missing = cleaned_df[column].notna()

            invalid_email = (
                non_missing
                & ~cleaned_df[column]
                .fillna("")
                .astype(str)
                .str.match(email_pattern)
            )

            invalid_mask |= invalid_email

    # 3. Date validation

    for column in cleaned_df.columns:

        column_lower = column.lower()

        if any(
            keyword in column_lower
            for keyword in ["date", "time", "timestamp"]
        ):

            converted_dates = pd.to_datetime(
                cleaned_df[column],
                errors="coerce"
            )

            invalid_date = (
                cleaned_df[column].notna()
                & converted_dates.isna()
            )

            invalid_mask |= invalid_date

    # 4. Separate invalid records

    quarantine_df = cleaned_df[invalid_mask].copy()

    cleaned_df = cleaned_df[~invalid_mask].copy()

    # 5. Remove duplicates

    before_duplicates = len(cleaned_df)

    cleaned_df = cleaned_df.drop_duplicates()

    duplicates_removed = (
        before_duplicates - len(cleaned_df)
    )

    return (
        cleaned_df,
        quarantine_df,
        duplicates_removed
    )


def save_cleaning_outputs(
    cleaned_df,
    quarantine_df,
    duplicates_removed,
    original_rows,
    processed_path="data/processed",
    quarantine_path="data/quarantine",
    report_path="data/cleaning_report.json"
):
    """
    Save cleaned data, quarantined data,
    and cleaning metrics/report.
    """

    processed_path = Path(processed_path)
    quarantine_path = Path(quarantine_path)
    report_path = Path(report_path)

    # Create directories

    processed_path.mkdir(
        parents=True,
        exist_ok=True
    )

    quarantine_path.mkdir(
        parents=True,
        exist_ok=True
    )

    # Calculate metrics

    quarantined_rows = len(quarantine_df)
    cleaned_rows = len(cleaned_df)

    retention_rate = round(
        (cleaned_rows / original_rows) * 100,
        2
    ) if original_rows > 0 else 0.0

    # Save cleaned data

    cleaned_file = (
        processed_path / "cleaned_data.csv"
    )

    cleaned_df.to_csv(
        cleaned_file,
        index=False
    )

    # Save quarantined data

    quarantine_file = (
        quarantine_path / "quarantined_data.csv"
    )

    quarantine_df.to_csv(
        quarantine_file,
        index=False
    )

    # Create cleaning report

    cleaning_report = {
        "original_rows": original_rows,
        "quarantined_rows": quarantined_rows,
        "duplicates_removed": duplicates_removed,
        "cleaned_rows": cleaned_rows,
        "retention_rate": retention_rate
    }

    with open(report_path, "w") as file:

        json.dump(
            cleaning_report,
            file,
            indent=4
        )

    print("\n===== CLEANING SUMMARY =====")

    print(
        "Original rows:",
        original_rows
    )

    print(
        "Invalid/quarantined rows:",
        quarantined_rows
    )

    print(
        "Duplicates removed:",
        duplicates_removed
    )

    print(
        "Final cleaned rows:",
        cleaned_rows
    )

    print(
        "Data retention rate:",
        retention_rate,
        "%"
    )

    print(
        "\nCleaned data saved to:",
        cleaned_file
    )

    print(
        "Quarantined data saved to:",
        quarantine_file
    )

    print(
        "Cleaning report saved to:",
        report_path
    )

    return cleaning_report


# Standalone Testing

if __name__ == "__main__":

    file_path = "data/raw/ecommerce_data.csv"

    df = pd.read_csv(file_path)

    cleaned_df, quarantine_df, duplicates_removed = (
        clean_dataset(df)
    )

    save_cleaning_outputs(
        cleaned_df,
        quarantine_df,
        duplicates_removed,
        original_rows=len(df)
    )

    print("\n===== QUARANTINE PREVIEW =====")

    print(
        quarantine_df.head()
    )
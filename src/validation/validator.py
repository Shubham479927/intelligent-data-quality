import pandas as pd
import json
from pathlib import Path


def validate_dataset(df):
    """
    Run generic data quality validation checks on a dataset.
    """

    results = {}

    results["total_rows"] = len(df)
    results["total_columns"] = len(df.columns)

    # 1. Missing Value Validation

    missing_results = {}

    for column in df.columns:

        missing_count = int(df[column].isna().sum())

        missing_results[column] = {
            "missing_count": missing_count,
            "status": "FAIL" if missing_count > 0 else "PASS"
        }

    results["missing_values"] = missing_results

    # 2. Duplicate Validation

    duplicate_count = int(df.duplicated().sum())

    results["duplicates"] = {
        "count": duplicate_count,
        "status": "FAIL" if duplicate_count > 0 else "PASS"
    }

    # 3. Numeric Range Validation

    range_results = {}

    numeric_columns = df.select_dtypes(
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

        invalid_count = int((df[column] < 0).sum())

        range_results[column] = {
            "invalid_count": invalid_count,
            "status": "FAIL" if invalid_count > 0 else "PASS"
        }

    results["range_validation"] = range_results

    # 4. Format Validation

    format_results = {}

    for column in df.columns:

        column_lower = column.lower()

        # Email validation

        if "email" in column_lower:

            email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

            non_missing_values = (
                df[column]
                .dropna()
                .astype(str)
            )

            invalid_count = int(
                (~non_missing_values.str.match(email_pattern)).sum()
            )

            format_results[column] = {
                "invalid_count": invalid_count,
                "status": "FAIL" if invalid_count > 0 else "PASS"
            }

        # Date validation

        elif any(
            keyword in column_lower
            for keyword in ["date", "time", "timestamp"]
        ):

            converted_values = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            invalid_count = int(
                converted_values.isna().sum()
            )

            format_results[column] = {
                "invalid_count": invalid_count,
                "status": "FAIL" if invalid_count > 0 else "PASS"
            }

    results["format_validation"] = format_results

    # 5. Schema Validation

    actual_columns = list(df.columns)

    schema_status = (
        "PASS"
        if len(actual_columns) > 0
        else "FAIL"
    )

    results["schema_validation"] = {
        "columns": actual_columns,
        "status": schema_status
    }

    # 6. Overall Data Quality Score

    checks = []

    # Missing value checks

    for result in results["missing_values"].values():
        checks.append(
            result["status"] == "PASS"
        )

    # Duplicate check

    checks.append(
        results["duplicates"]["status"] == "PASS"
    )

    # Range checks

    for result in results["range_validation"].values():
        checks.append(
            result["status"] == "PASS"
        )

    # Format checks

    for result in results["format_validation"].values():
        checks.append(
            result["status"] == "PASS"
        )

    # Schema check

    checks.append(
        results["schema_validation"]["status"] == "PASS"
    )

    passed_checks = sum(checks)
    total_checks = len(checks)

    if total_checks > 0:
        quality_score = round(
            (passed_checks / total_checks) * 100,
            2
        )
    else:
        quality_score = 0.0

    overall_status = (
        "PASS"
        if quality_score == 100
        else "FAIL"
    )

    results["quality_score"] = quality_score
    results["overall_status"] = overall_status

    return results


def save_validation_report(
    results,
    output_path="data/validation_report.json"
):
    """
    Save validation results as a JSON report.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(output_path, "w") as file:
        json.dump(
            results,
            file,
            indent=4
        )

    print(
        "\nValidation report saved to:",
        output_path
    )


# Standalone Testing

if __name__ == "__main__":

    file_path = "data/raw/ecommerce_data.csv"

    df = pd.read_csv(file_path)

    results = validate_dataset(df)

    print("\n===== DATA QUALITY VALIDATION =====")

    print(
        "Total rows:",
        results["total_rows"]
    )

    print(
        "Total columns:",
        results["total_columns"]
    )

    print("\n===== MISSING VALUE CHECK =====")

    for column, result in results["missing_values"].items():

        print(
            f"{column}: "
            f"{result['missing_count']} missing → "
            f"{result['status']}"
        )

    print("\n===== DUPLICATE CHECK =====")

    print(
        "Duplicates:",
        results["duplicates"]["count"],
        "→",
        results["duplicates"]["status"]
    )

    print("\n===== RANGE VALIDATION =====")

    for column, result in results["range_validation"].items():

        print(
            f"{column}: "
            f"{result['invalid_count']} invalid → "
            f"{result['status']}"
        )

    print("\n===== FORMAT VALIDATION =====")

    for column, result in results["format_validation"].items():

        print(
            f"{column}: "
            f"{result['invalid_count']} invalid → "
            f"{result['status']}"
        )

    print("\n===== SCHEMA VALIDATION =====")

    schema = results["schema_validation"]

    print(
        "Columns:",
        schema["columns"]
    )

    print(
        "Status:",
        schema["status"]
    )

    print("\n===== OVERALL DATA QUALITY =====")

    print(
        "Quality Score:",
        results["quality_score"],
        "%"
    )

    print(
        "Overall Status:",
        results["overall_status"]
    )

    # Save Validation Report

    save_validation_report(results)
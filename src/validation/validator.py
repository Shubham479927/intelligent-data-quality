import pandas as pd
import json


def validate_dataset(df):
    """
    Run data quality validation checks on a dataset.
    """

    results = {}

    results["total_rows"] = len(df)
    results["total_columns"] = len(df.columns)

    # Missing value validation
    missing_results = {}

    for column in df.columns:
        missing_count = int(df[column].isna().sum())

        if missing_count > 0:
            status = "FAIL"
        else:
            status = "PASS"

        missing_results[column] = {
            "missing_count": missing_count,
            "status": status
        }

    results["missing_values"] = missing_results

    # Duplicate validation
    duplicate_count = int(df.duplicated().sum())

    results["duplicates"] = {
        "count": duplicate_count,
        "status": "FAIL" if duplicate_count > 0 else "PASS"
    }
    
        # Range validation
    range_results = {}

    # Quantity validation
    invalid_quantity = int((df["quantity"] <= 0).sum())

    range_results["quantity"] = {
        "invalid_count": invalid_quantity,
        "status": "FAIL" if invalid_quantity > 0 else "PASS"
    }

    # Unit price validation
    invalid_price = int((df["unit_price"] <= 0).sum())

    range_results["unit_price"] = {
        "invalid_count": invalid_price,
        "status": "FAIL" if invalid_price > 0 else "PASS"
    }

    # Customer age validation
    invalid_age = int(
        ((df["customer_age"] < 18) | (df["customer_age"] > 100)).sum()
    )

    range_results["customer_age"] = {
        "invalid_count": invalid_age,
        "status": "FAIL" if invalid_age > 0 else "PASS"
    }

    results["range_validation"] = range_results
    
        # Format validation
    format_results = {}

    # Email validation
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"

    invalid_email = int(
        (~df["customer_email"].fillna("").str.match(email_pattern)).sum()
    )

    format_results["customer_email"] = {
        "invalid_count": invalid_email,
        "status": "FAIL" if invalid_email > 0 else "PASS"
    }

    # Date validation
    converted_dates = pd.to_datetime(
        df["order_date"],
        errors="coerce"
    )

    invalid_dates = int(converted_dates.isna().sum())

    format_results["order_date"] = {
        "invalid_count": invalid_dates,
        "status": "FAIL" if invalid_dates > 0 else "PASS"
    }

    results["format_validation"] = format_results
    
        # Schema validation
    expected_columns = [
        "order_id",
        "customer_id",
        "order_date",
        "product_category",
        "quantity",
        "unit_price",
        "total_amount",
        "payment_method",
        "customer_age",
        "customer_email"
    ]

    actual_columns = list(df.columns)

    missing_columns = [
        column for column in expected_columns
        if column not in actual_columns
    ]

    unexpected_columns = [
        column for column in actual_columns
        if column not in expected_columns
    ]

    schema_status = (
        "PASS"
        if not missing_columns and not unexpected_columns
        else "FAIL"
    )

    results["schema_validation"] = {
        "missing_columns": missing_columns,
        "unexpected_columns": unexpected_columns,
        "status": schema_status
    }
    
        # Overall data quality score

    checks = []

    # Missing value checks
    for result in results["missing_values"].values():
        checks.append(result["status"] == "PASS")

    # Duplicate check
    checks.append(results["duplicates"]["status"] == "PASS")

    # Range checks
    for result in results["range_validation"].values():
        checks.append(result["status"] == "PASS")

    # Format checks
    for result in results["format_validation"].values():
        checks.append(result["status"] == "PASS")

    # Schema check
    checks.append(results["schema_validation"]["status"] == "PASS")

    passed_checks = sum(checks)
    total_checks = len(checks)

    quality_score = round(
        (passed_checks / total_checks) * 100,
        2
    )

    overall_status = (
        "PASS"
        if quality_score == 100
        else "FAIL"
    )

    results["quality_score"] = quality_score
    results["overall_status"] = overall_status
    
    return results


if __name__ == "__main__":

    file_path = "data/raw/ecommerce_data.csv"

    df = pd.read_csv(file_path)

    results = validate_dataset(df)

    print("\n===== DATA QUALITY VALIDATION =====")

    print("Total rows:", results["total_rows"])
    print("Total columns:", results["total_columns"])

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

    print("Missing columns:", schema["missing_columns"])
    print("Unexpected columns:", schema["unexpected_columns"])
    print("Status:", schema["status"])
    
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
    
        # Save validation report
    output_path = "data/validation_report.json"

    with open(output_path, "w") as file:
        json.dump(results, file, indent=4)

    print("\nValidation report saved to:", output_path)
import pandas as pd
import json
import yaml
from pathlib import Path

def load_validation_rules(
    config_path="config/validation_rules.yaml"
):
    """
    Load data validation rules from a YAML configuration file.
    """

    config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Validation rules file not found: {config_path}"
        )

    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    return config

def validate_dataset(df):
    """
    Run generic data quality validation checks on a dataset.
    """

    config = load_validation_rules()
    rules = config.get("rules", {})

    results = {}

    results["total_rows"] = len(df)
    results["total_columns"] = len(df.columns)

    # 1. Missing Value Validation

    missing_results = {}

    for column in df.columns:

        missing_count = int(df[column].isna().sum())

        column_rules = rules.get(column, {})

        required = column_rules.get("required", False)

        if required:
            status = "FAIL" if missing_count > 0 else "PASS"
        else:
            status = "PASS"

        missing_results[column] = {
            "missing_count": missing_count,
            "status": status
        }

    results["missing_values"] = missing_results

    # 2. Duplicate Validation

    duplicate_count = int(df.duplicated().sum())

    duplicate_rules = config.get("duplicate_check", {})
    duplicates_allowed = duplicate_rules.get("allowed", False)

    if duplicates_allowed:
        duplicate_status = "PASS"
    else:
        duplicate_status = (
            "FAIL"
            if duplicate_count > 0
            else "PASS"
        )

    results["duplicates"] = {
        "count": duplicate_count,
        "allowed": duplicates_allowed,
        "status": duplicate_status
    }

    # 3. Numeric Range Validation

    range_results = {}

    numeric_columns = df.select_dtypes(
        include=["number"]
    ).columns

    for column in numeric_columns:

        if column not in rules:
            continue

        column_rules = rules[column]

        invalid_mask = pd.Series(
            False,
            index=df.index
        )

        if "min" in column_rules:
            invalid_mask |= df[column] < column_rules["min"]

        if "max" in column_rules:
            invalid_mask |= df[column] > column_rules["max"]

        invalid_count = int(invalid_mask.sum())

        range_results[column] = {
            "invalid_count": invalid_count,
            "status": "FAIL" if invalid_count > 0 else "PASS"
        }

    results["range_validation"] = range_results

    # 3.5 Allowed Values Validation

    allowed_values_results = {}

    for column, column_rules in rules.items():

        if "allowed_values" not in column_rules:
            continue

        if column not in df.columns:
            continue

        allowed_values = column_rules["allowed_values"]

        invalid_mask = ~df[column].isin(allowed_values)

        invalid_count = int(invalid_mask.sum())

        allowed_values_results[column] = {
            "allowed_values": allowed_values,
            "invalid_count": invalid_count,
            "status": "FAIL" if invalid_count > 0 else "PASS"
        }

    results["allowed_values_validation"] = allowed_values_results

    # 4. Format Validation

    format_results = {}

    for column in df.columns:

        column_rules = rules.get(column, {})

        data_type = column_rules.get("type")

        # Email validation
        if data_type == "email":

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
        elif data_type == "date":

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

    schema_rules = config.get("schema", {})

    required_columns = schema_rules.get(
        "required_columns",
        []
    )

    actual_columns = list(df.columns)

    missing_columns = [
        column
        for column in required_columns
        if column not in actual_columns
    ]

    unexpected_columns = [
        column
        for column in actual_columns
        if column not in required_columns
    ]

    schema_status = (
        "PASS"
        if not missing_columns and not unexpected_columns
        else "FAIL"
    )

    results["schema_validation"] = {
        "expected_columns": required_columns,
        "actual_columns": actual_columns,
        "missing_columns": missing_columns,
        "unexpected_columns": unexpected_columns,
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

    # Allowed values checks

    for result in results["allowed_values_validation"].values():
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

    print("\n===== ALLOWED VALUES VALIDATION =====")

    for column, result in results["allowed_values_validation"].items():

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
        "Expected columns:",
        schema["expected_columns"]
    )

    print(
        "Actual columns:",
        schema["actual_columns"]
    )

    print(
        "Missing columns:",
        schema["missing_columns"]
    )

    print(
        "Unexpected columns:",
        schema["unexpected_columns"]
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

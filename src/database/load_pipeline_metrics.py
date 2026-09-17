import json
from pathlib import Path

from .db_connection import get_engine
from sqlalchemy import text


def load_pipeline_metrics():
    validation_report_path = Path(
        "/opt/airflow/data/validation_report.json"
    )

    cleaning_report_path = Path(
        "/opt/airflow/data/cleaning_report.json"
    )

    with open(validation_report_path, "r") as file:
        validation_report = json.load(file)

    with open(cleaning_report_path, "r") as file:
        cleaning_report = json.load(file)

    metrics = {
        "original_rows": cleaning_report["original_rows"],
        "quarantined_rows": cleaning_report["quarantined_rows"],
        "duplicates_removed": cleaning_report["duplicates_removed"],
        "cleaned_rows": cleaning_report["cleaned_rows"],
        "retention_rate": cleaning_report["retention_rate"],
        "quality_score": validation_report["quality_score"],
        "pipeline_status": validation_report["overall_status"],
    }

    engine = get_engine()

    with engine.begin() as connection:

        connection.execute(
                text("""
                INSERT INTO pipeline_metrics (
                    original_rows,
                    quarantined_rows,
                    duplicates_removed,
                    cleaned_rows,
                    retention_rate,
                    quality_score,
                    pipeline_status
                )
                VALUES (
                    :original_rows,
                    :quarantined_rows,
                    :duplicates_removed,
                    :cleaned_rows,
                    :retention_rate,
                    :quality_score,
                    :pipeline_status
                )
            """),
            metrics,
        )

    print("\nPipeline metrics loaded successfully!")
    print(metrics)


if __name__ == "__main__":
    load_pipeline_metrics()

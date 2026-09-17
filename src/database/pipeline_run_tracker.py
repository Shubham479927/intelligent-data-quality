from sqlalchemy import text
from .db_connection import get_engine


def start_pipeline_run():
    engine = get_engine()

    query = text("""
        INSERT INTO pipeline_runs (status)
        VALUES ('RUNNING')
    """)

    with engine.begin() as connection:
        result = connection.execute(query)
        run_id = result.lastrowid

    print(f"Pipeline run started. Run ID: {run_id}")

    return run_id

def mark_pipeline_failed(run_id, error_message):
    engine = get_engine()

    query = text("""
        UPDATE pipeline_runs
        SET
            end_time = CURRENT_TIMESTAMP,
            status = 'FAILED',
            error_message = :error_message
        WHERE run_id = :run_id
    """)

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "run_id": run_id,
                "error_message": error_message
            }
        )

    print(f"Pipeline run {run_id} marked as FAILED.")

def finish_pipeline_run(
    run_id,
    status,
    original_rows,
    cleaned_rows,
    quarantined_rows,
    duplicates_removed,
    anomaly_count,
    quality_score,
    error_message=None
):
    engine = get_engine()

    query = text("""
        UPDATE pipeline_runs
        SET
            end_time = CURRENT_TIMESTAMP,
            status = CASE
                WHEN status = 'FAILED' THEN 'FAILED'
                ELSE :status
            END,
            original_rows = :original_rows,
            cleaned_rows = :cleaned_rows,
            quarantined_rows = :quarantined_rows,
            duplicates_removed = :duplicates_removed,
            anomaly_count = :anomaly_count,
            quality_score = :quality_score,
            error_message = CASE
                WHEN status = 'FAILED' THEN error_message
                ELSE :error_message
            END
        WHERE run_id = :run_id
    """)

    with engine.begin() as connection:
        connection.execute(
            query,
            {
                "run_id": run_id,
                "status": status,
                "original_rows": original_rows,
                "cleaned_rows": cleaned_rows,
                "quarantined_rows": quarantined_rows,
                "duplicates_removed": duplicates_removed,
                "anomaly_count": anomaly_count,
                "quality_score": quality_score,
                "error_message": error_message
            }
        )

    print(f"Pipeline run {run_id} finished with status: {status}")

if __name__ == "__main__":
    start_pipeline_run()

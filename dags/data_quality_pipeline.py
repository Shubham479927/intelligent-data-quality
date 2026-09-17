from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime
from src.database.pipeline_run_tracker import start_pipeline_run




from src.ingestion.ingest import ingest_csv
from src.profiling.profiler import profile_dataset
from src.validation.validator import (
    validate_dataset,
    save_validation_report,
)
from src.cleaning.cleaner import (
    clean_dataset,
    save_cleaning_outputs,
)
from src.anomaly_detection.anomaly_detector import (
    load_data as load_anomaly_data,
    select_features,
    preprocess_features,
    train_model,
    detect_anomalies,
    calculate_anomaly_scores,
    save_results,
)

from src.database.load_data import load_data as load_database_data
from src.database.load_pipeline_metrics import load_pipeline_metrics


def start_pipeline(**context):
    run_id = start_pipeline_run()

    context["ti"].xcom_push(
        key="pipeline_run_id",
        value=run_id
    )

    print(f"Pipeline Run ID: {run_id}")


def run_ingestion():
    df = ingest_csv("/opt/airflow/data/raw/ecommerce_data.csv")

    original_rows = len(df)

    print(f"Original rows: {original_rows}")

    return original_rows


def run_profiling():
    df = ingest_csv("/opt/airflow/data/raw/ecommerce_data.csv")
    profile_dataset(df)

def run_validation():

    df = ingest_csv(
        "/opt/airflow/data/raw/ecommerce_data.csv"
    )

    results = validate_dataset(df)

    save_validation_report(
        results,
        "/opt/airflow/data/validation_report.json"
    )

    quality_score = results["quality_score"]

    print(f"Data quality score: {quality_score}")

    return quality_score

def run_cleaning():

    df = ingest_csv(
        "/opt/airflow/data/raw/ecommerce_data.csv"
    )

    cleaned_df, quarantine_df, duplicates_removed = (
        clean_dataset(df)
    )

    save_cleaning_outputs(
        cleaned_df,
        quarantine_df,
        duplicates_removed,
        original_rows=len(df),
        processed_path="/opt/airflow/data/processed",
        quarantine_path="/opt/airflow/data/quarantine",
        report_path="/opt/airflow/data/cleaning_report.json"
    )

    return {
        "cleaned_rows": len(cleaned_df),
        "quarantined_rows": len(quarantine_df),
        "duplicates_removed": duplicates_removed
    }

def run_anomaly_detection():
    df = load_anomaly_data()

    X = select_features(df)

    X = preprocess_features(X)

    model = train_model(X)

    predictions = detect_anomalies(model, X)

    scores = calculate_anomaly_scores(model, X)

    save_results(df, X, predictions, scores)

    anomaly_count = int((predictions == -1).sum())

    print(f"Anomalies detected: {anomaly_count}")

    return anomaly_count

def run_database_load():
    load_database_data()

def run_pipeline_metrics():
    load_pipeline_metrics()

def handle_task_failure(context):
    ti = context["ti"]

    run_id = ti.xcom_pull(
        task_ids="start_pipeline",
        key="pipeline_run_id"
    )

    task_id = ti.task_id
    error = str(context.get("exception"))

    print(f"Task failed: {task_id}")
    print(f"Error: {error}")

    if run_id is not None:
        from src.database.pipeline_run_tracker import mark_pipeline_failed

        mark_pipeline_failed(
            run_id=run_id,
            error_message=f"{task_id}: {error}"
        )

def finish_pipeline(**context):
    from src.database.pipeline_run_tracker import finish_pipeline_run

    ti = context["ti"]

    run_id = ti.xcom_pull(
        task_ids="start_pipeline",
        key="pipeline_run_id"
    )

    original_rows = ti.xcom_pull(task_ids="ingestion")

    cleaning_metrics = ti.xcom_pull(task_ids="cleaning")

    cleaned_rows = cleaning_metrics["cleaned_rows"]
    quarantined_rows = cleaning_metrics["quarantined_rows"]
    duplicates_removed = cleaning_metrics["duplicates_removed"]

    anomaly_count = ti.xcom_pull(task_ids="anomaly_detection")
    quality_score = ti.xcom_pull(task_ids="validation")

    print(f"Finishing Pipeline Run ID: {run_id}")

    finish_pipeline_run(
        run_id=run_id,
        status="SUCCESS",
        original_rows=original_rows,
        cleaned_rows=cleaned_rows,
        quarantined_rows=quarantined_rows,
        duplicates_removed=duplicates_removed,
        anomaly_count=anomaly_count,
        quality_score=quality_score,
        error_message=None,
    )
default_args = {
    "on_failure_callback": handle_task_failure
}

with DAG(
    dag_id="data_quality_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    default_args=default_args,
) as dag:

    start = PythonOperator(
        task_id="start_pipeline",
        python_callable=start_pipeline,
    )

    ingestion = PythonOperator(
        task_id="ingestion",
        python_callable=run_ingestion,
    )

    profiling = PythonOperator(
        task_id="profiling",
        python_callable=run_profiling,
    )

    validation = PythonOperator(
        task_id="validation",
        python_callable=run_validation,
    )

    cleaning = PythonOperator(
        task_id="cleaning",
        python_callable=run_cleaning,
    )

    anomaly_detection = PythonOperator(
        task_id="anomaly_detection",
        python_callable=run_anomaly_detection,
    )

    database_load = PythonOperator(
        task_id="database_load",
        python_callable=run_database_load,
    )

    pipeline_metrics = PythonOperator(
        task_id="pipeline_metrics",
        python_callable=run_pipeline_metrics,
    )

    finish = PythonOperator(
        task_id="finish_pipeline",
        python_callable=finish_pipeline,
        trigger_rule=TriggerRule.ALL_DONE,
    )


    start >> ingestion >> profiling >> validation >> cleaning >> anomaly_detection >> database_load >> pipeline_metrics >> finish

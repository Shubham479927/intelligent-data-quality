from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from datetime import datetime



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


def start_pipeline():
    print("Intelligent Data Quality Pipeline Started!")


def run_ingestion():
    ingest_csv("/opt/airflow/data/raw/ecommerce_data.csv")


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
    
def run_anomaly_detection():
    df = load_anomaly_data()

    X = select_features(df)

    X = preprocess_features(X)

    model = train_model(X)

    predictions = detect_anomalies(model, X)

    scores = calculate_anomaly_scores(model, X)

    save_results(df, predictions, scores)

def run_database_load():
    load_database_data()
    
def run_pipeline_metrics():
    load_pipeline_metrics()

with DAG(
    dag_id="data_quality_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
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
    
    start >> ingestion >> profiling >> validation >> cleaning >> anomaly_detection >> database_load >> pipeline_metrics
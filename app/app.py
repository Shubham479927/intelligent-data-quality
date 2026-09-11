import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
from src.validation.validator import validate_dataset
from src.cleaning.cleaner import clean_dataset
from src.anomaly_detection.anomaly_detector import (
    select_features,
    preprocess_features,
    train_model,
    detect_anomalies,
    calculate_anomaly_scores,
)
from src.database.load_anomaly_results import load_anomaly_results
from src.database.load_data import load_data as load_database_data


st.set_page_config(
    page_title="Intelligent Data Quality Platform",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Intelligent Data Quality & Anomaly Detection Platform")

st.write(
    "Upload a dataset to analyze data quality, clean invalid records, "
    "and detect anomalies."
)

st.divider()

st.header("Upload Dataset")

uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    st.success("File uploaded successfully!")


    df = pd.read_csv(uploaded_file)

    st.write("File name:", uploaded_file.name)

    st.subheader("Dataset Preview")

    st.dataframe(df.head())
    st.subheader("Dataset Information")

    col1, col2 = st.columns(2)

    col1.metric("Rows", df.shape[0])
    col2.metric("Columns", df.shape[1])
    

    missing_values = df.isnull().sum()

    st.subheader("Missing Values")

    missing_values = df.isnull().sum()

    st.dataframe(missing_values)

    st.subheader("Data Quality")


    validation_report = validate_dataset(df)

    quality_score = validation_report["quality_score"]

    st.metric(
        "Data Quality Score",
        f"{quality_score:.1f}%"
    )
    
    st.progress(
        quality_score / 100
    )
    
    st.subheader("Validation Checks")

    validation_sections = [
        "missing_values",
        "duplicates",
        "range_validation",
        "format_validation",
        "schema_validation"
    ]

    for section in validation_sections:
        st.write(f"**{section.replace('_', ' ').title()}**")

        section_data = validation_report[section]

        if isinstance(section_data, dict):

            if "status" in section_data:
                status = section_data["status"]

                if status == "PASS":
                    st.success("✅ Schema validation passed")
                else:
                    st.error("❌ Schema validation failed")

            else:
                for check_name, check_result in section_data.items():

                    if isinstance(check_result, dict):
                        status = check_result.get("status")

                        if status == "PASS":
                            st.success(f"✅ {check_name}")
                        else:
                            st.error(f"❌ {check_name}")
    
    st.subheader("Cleaning Results")

    cleaned_df, quarantined_df, duplicates_removed = clean_dataset(df)

    cleaned_rows = len(cleaned_df)
    quarantined_rows = len(quarantined_df)

    col1, col2 = st.columns(2)

    col1.metric(
        "Cleaned Records",
        cleaned_rows
    )

    col2.metric(
        "Quarantined Records",
        quarantined_rows
    )
    
    st.subheader("Cleaned Data Preview")

    st.dataframe(cleaned_df.head(10))
    
    csv_data = cleaned_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Cleaned Data",
        data=csv_data,
        file_name="cleaned_data.csv",
        mime="text/csv"
    )
    
    st.subheader("Anomaly Detection")

    try:
        X = select_features(cleaned_df)

        X = preprocess_features(X)

    except ValueError:
        st.warning(
            "⚠️ Anomaly detection skipped because the dataset "
            "does not contain suitable numeric features."
        )
        st.stop()

    model = train_model(X)

    predictions = detect_anomalies(model, X)

    scores = calculate_anomaly_scores(model, X)
    
    results_df = cleaned_df.copy()

    results_df["anomaly_prediction"] = predictions
    results_df["anomaly_score"] = scores

    results_df["anomaly_status"] = results_df["anomaly_prediction"].map({
        1: "Normal",
        -1: "Anomaly"
    })
    
    normal_count = sum(predictions == 1)
    anomaly_count = sum(predictions == -1)
    
    anomaly_percentage = (
        anomaly_count / len(results_df)
    ) * 100

    results_df.to_csv(
        "data/anomaly_results.csv",
        index=False
    )
    
    if "order_id" in results_df.columns:

        load_database_data()
        load_anomaly_results()

    else:

        st.info(
            "ℹ️ MySQL loading skipped because this dataset "
            "does not contain an order_id column."
        )

    st.success("✅ Anomaly detection completed successfully!")
    
    
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Normal Records",
        normal_count
    )

    col2.metric(
        "Anomalous Records",
        anomaly_count
    )

    col3.metric(
        "Anomaly Rate",
        f"{anomaly_percentage:.2f}%"
    )
    
    st.subheader("📊 Pipeline Overview")

    total_records = len(df)

    kpi1, kpi2, kpi3 = st.columns(3)

    kpi1.metric(
        "Total Records",
        total_records
    )

    kpi2.metric(
        "Quality Score",
        f"{quality_score:.1f}%"
    )

    if validation_report["overall_status"] == "PASS":
        kpi2.success("Status: PASS")
    else:
        kpi2.error("Status: FAIL")

    kpi3.metric(
        "Cleaned Records",
        cleaned_rows
    )


    st.subheader("Detected Anomalies")

    anomaly_df = results_df[
        results_df["anomaly_status"] == "Anomaly"
    ]

    st.dataframe(anomaly_df)
    
    anomaly_csv = results_df.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="⬇️ Download Anomaly Results",
        data=anomaly_csv,
        file_name="anomaly_results.csv",
        mime="text/csv"
    )
    
    st.subheader("Anomaly Distribution")

    anomaly_distribution = results_df["anomaly_status"].value_counts()

    st.bar_chart(anomaly_distribution)
    
    st.subheader("Most Unusual Records")

    most_unusual = results_df.sort_values(
        by="anomaly_score"
    ).head(10)

    st.dataframe(most_unusual)
    
    st.divider()

    st.success("✅ Data analysis pipeline completed successfully!")
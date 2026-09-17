import pandas as pd
from sqlalchemy import text
from .db_connection import get_engine


def load_anomaly_results():

    file_path = "data/anomaly_results.csv"

    df = pd.read_csv(file_path)

    engine = get_engine()

    # Check existing order IDs
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT order_id FROM anomaly_results")
        )

        existing_ids = {row[0] for row in result}

    # Keep only new results
    new_df = df[
        ~df["order_id"].isin(existing_ids)
    ][
        [
            "order_id",
            "anomaly_prediction",
            "anomaly_score",
            "anomaly_status"
        ]
    ]

    if new_df.empty:
        print("No new anomaly results to load.")
        return

    new_df.to_sql(
        "anomaly_results",
        con=engine,
        if_exists="append",
        index=False
    )

    print("Anomaly results loaded successfully!")
    print("Rows loaded:", len(new_df))


if __name__ == "__main__":
    load_anomaly_results()

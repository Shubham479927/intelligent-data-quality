import pandas as pd
from sqlalchemy import text
from .db_connection import get_engine


def load_data():

    file_path = "data/processed/cleaned_data.csv"

    df = pd.read_csv(file_path)

    engine = get_engine()

    # Get existing order IDs from database
    with engine.connect() as connection:

        result = connection.execute(
            text("SELECT order_id FROM orders")
        )

        existing_ids = {row[0] for row in result}

    # Keep only new records
    new_df = df[~df["order_id"].isin(existing_ids)]

    if new_df.empty:

        print("No new data to load.")
        print("All records already exist in MySQL.")
        return

    # Insert only new records
    new_df.to_sql(
        "orders",
        con=engine,
        if_exists="append",
        index=False
    )

    print("New data loaded successfully!")
    print("New rows loaded:", len(new_df))


if __name__ == "__main__":
    load_data()
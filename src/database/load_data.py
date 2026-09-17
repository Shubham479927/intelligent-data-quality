import re
import pandas as pd
from sqlalchemy import inspect, text
from .db_connection import get_engine

def validate_identifier(value):
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        raise ValueError(f"Invalid database identifier: {value}")
    return value

def load_data(
    table_name="orders",
    primary_key="order_id",
    file_path="data/processed/cleaned_data.csv"
):

    table_name = validate_identifier(table_name)
    primary_key = validate_identifier(primary_key)

    if not table_name:
        raise ValueError("Table name cannot be empty.")

    if not primary_key:
        raise ValueError("Primary key cannot be empty.")

    df = pd.read_csv(file_path)

    if primary_key not in df.columns:
        raise ValueError(
            f"Primary key '{primary_key}' not found in dataset."
        )

    if df[primary_key].isna().any():
        raise ValueError(
            f"Primary key '{primary_key}' contains missing values."
        )

    if df[primary_key].duplicated().any():
        raise ValueError(
            f"Primary key '{primary_key}' contains duplicate values."
        )

    engine = get_engine()

    inspector = inspect(engine)

    if not inspector.has_table(table_name):
        raise ValueError(
            f"Table '{table_name}' does not exist in the database."
        )

    # Get existing primary keys from database

    with engine.connect() as connection:

        result = connection.execute(
            text(f"SELECT `{primary_key}` FROM `{table_name}`")
        )

        existing_ids = {row[0] for row in result}

    # Keep only new records
    new_df = df[~df[primary_key].isin(existing_ids)]

    if new_df.empty:

        print("No new data to load.")
        print("All records already exist in MySQL.")
        return

    # Insert only new records
    new_df.to_sql(table_name, con=engine, if_exists="append", index=False)

    print("New data loaded successfully!")
    print("New rows loaded:", len(new_df))


if __name__ == "__main__":
    load_data(
        table_name="orders",
        primary_key="order_id"
    )

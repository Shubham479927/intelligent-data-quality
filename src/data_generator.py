import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta


def generate_dataset(n_records=1000, bad_data=True):
    random.seed(42)
    np.random.seed(42)

    categories = [
        "Electronics",
        "Clothing",
        "Home",
        "Books",
        "Beauty",
        "Sports"
    ]

    payment_methods = [
        "Credit Card",
        "Debit Card",
        "UPI",
        "Cash",
        "Net Banking"
    ]

    records = []

    start_date = datetime(2026, 1, 1)

    for i in range(n_records):

        quantity = random.randint(1, 10)
        unit_price = round(random.uniform(50, 5000), 2)

        record = {
            "order_id": 10000 + i,
            "customer_id": random.randint(500, 1500),
            "order_date": (
                start_date + timedelta(days=random.randint(0, 180))
            ).strftime("%Y-%m-%d"),
            "product_category": random.choice(categories),
            "quantity": quantity,
            "unit_price": unit_price,
            "total_amount": round(quantity * unit_price, 2),
            "payment_method": random.choice(payment_methods),
            "customer_age": random.randint(18, 70),
            "customer_email": f"customer{i}@gmail.com"
        }

        records.append(record)

    df = pd.DataFrame(records)

    # Add controlled data quality problems
    if bad_data:

        # Missing values
        missing_indices = np.random.choice(
            df.index,
            size=int(n_records * 0.03),
            replace=False
        )

        df.loc[missing_indices, "customer_email"] = np.nan

        # Duplicate records
        duplicate_count = max(1, int(n_records * 0.02))
        duplicates = df.sample(duplicate_count, random_state=42)

        df = pd.concat([df, duplicates], ignore_index=True)

        # Invalid quantity
        invalid_quantity_indices = np.random.choice(
            df.index,
            size=max(1, int(n_records * 0.01)),
            replace=False
        )

        df.loc[invalid_quantity_indices, "quantity"] = -5

        # Invalid price
        invalid_price_indices = np.random.choice(
            df.index,
            size=max(1, int(n_records * 0.01)),
            replace=False
        )

        df.loc[invalid_price_indices, "unit_price"] = -100

        # Invalid age
        invalid_age_indices = np.random.choice(
            df.index,
            size=max(1, int(n_records * 0.01)),
            replace=False
        )

        df.loc[invalid_age_indices, "customer_age"] = 150

        # Invalid email
        invalid_email_indices = np.random.choice(
            df.index,
            size=max(1, int(n_records * 0.01)),
            replace=False
        )

        df.loc[invalid_email_indices, "customer_email"] = "invalid_email"

        # Invalid date
        invalid_date_indices = np.random.choice(
            df.index,
            size=max(1, int(n_records * 0.01)),
            replace=False
        )

        df.loc[invalid_date_indices, "order_date"] = "INVALID_DATE"

    return df


if __name__ == "__main__":

    df = generate_dataset(
        n_records=1000,
        bad_data=True
    )

    output_path = "data/raw/ecommerce_data.csv"

    df.to_csv(output_path, index=False)

    print("Dataset generated successfully!")
    print("Rows:", len(df))
    print("Columns:", len(df.columns))
    print("Saved to:", output_path)
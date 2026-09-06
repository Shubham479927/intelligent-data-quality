import pandas as pd
from pathlib import Path
import json


def profile_dataset(df):
    """
    Generate profiling information for a dataset.
    """

    profile = {}

    # Basic dataset information
    profile["rows"] = len(df)
    profile["columns"] = len(df.columns)

    column_info = []

    for column in df.columns:

        info = {
            "column": column,
            "data_type": str(df[column].dtype),
            "missing_values": int(df[column].isna().sum()),
            "unique_values": int(df[column].nunique())
        }

        # Numeric statistics
        if pd.api.types.is_numeric_dtype(df[column]):

            info["column_type"] = "numeric"
            info["min"] = df[column].min()
            info["max"] = df[column].max()
            info["mean"] = round(df[column].mean(), 2)
            info["median"] = df[column].median()
            info["std"] = round(df[column].std(), 2)

        # Categorical information
        else:

            info["column_type"] = "categorical"

            value_counts = (
                df[column]
                .value_counts(dropna=False)
                .head(10)
                .to_dict()
            )

            info["top_values"] = value_counts

        column_info.append(info)

    profile["columns_info"] = column_info

    # Duplicate information
    profile["duplicate_rows"] = int(df.duplicated().sum())

    return profile

import sys

if __name__ == "__main__":

   
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "data/raw/ecommerce_data.csv"

    if not Path(file_path).exists():

        print("ERROR: Dataset not found.")

    else:

        df = pd.read_csv(file_path)

        profile = profile_dataset(df)

        print("\n===== DATASET PROFILE =====")

        print("Rows:", profile["rows"])
        print("Columns:", profile["columns"])
        print("Duplicate rows:", profile["duplicate_rows"])

        print("\n===== COLUMN INFORMATION =====")

        for column in profile["columns_info"]:

            print(
                f"\n{column['column']} | "
                f"Type: {column['data_type']} | "
                f"Category: {column['column_type']} | "
                f"Missing: {column['missing_values']} | "
                f"Unique: {column['unique_values']}"
            )

            if column["column_type"] == "numeric":

                print(
                    f"   Min: {column['min']} | "
                    f"Max: {column['max']} | "
                    f"Mean: {column['mean']} | "
                    f"Median: {column['median']} | "
                    f"Std: {column['std']}"
                )

            else:

                print("   Top values:")

                for value, count in column["top_values"].items():

                    print(f"      {value}: {count}")
            
                    # Save profiling results
        output_path = Path("data/profiling_report.json")

        output_path.parent.mkdir(exist_ok=True)

        with open(output_path, "w") as file:
            json.dump(profile, file, indent=4, default=str)

        print("\nProfiling report saved to:", output_path)
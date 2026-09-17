import pandas as pd
from pathlib import Path
import logging


# Create logs directory
Path("logs").mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    filename="logs/ingestion.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def ingest_csv(file_path):
    """
    Read a CSV file and return it as a Pandas DataFrame.
    """

    file_path = Path(file_path)

    try:

        if not file_path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        df = pd.read_csv(file_path)

        logger.info(
            f"Successfully ingested file: {file_path}"
        )

        logger.info(
            f"Rows: {len(df)}, Columns: {len(df.columns)}"
        )

        print("Data ingestion successful!")
        print("Rows:", len(df))
        print("Columns:", len(df.columns))

        return df

    except FileNotFoundError as error:

        logger.error(str(error))
        print("ERROR:", error)

    except Exception as error:

        logger.exception(
            f"Unexpected error while ingesting file: {error}"
        )
        print("ERROR:", error)


if __name__ == "__main__":

    file_path = "data/raw/ecommerce_data.csv"

    df = ingest_csv(file_path)

    if df is not None:
        print("\nFirst 5 rows:")
        print(df.head())

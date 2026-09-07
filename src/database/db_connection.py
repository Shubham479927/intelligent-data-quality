import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()


def get_engine():

    username = os.getenv("MYSQL_USER")
    password = os.getenv("MYSQL_PASSWORD")
    host = os.getenv("MYSQL_HOST")
    database = os.getenv("MYSQL_DATABASE")

    connection_url = (
        f"mysql+pymysql://{username}:{password}@{host}/{database}"
    )

    engine = create_engine(connection_url)

    return engine


if __name__ == "__main__":

    engine = get_engine()

    with engine.connect() as connection:
        print("MySQL connection successful!")
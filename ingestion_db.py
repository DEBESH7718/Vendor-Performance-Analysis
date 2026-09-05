import os
import time
import logging
import pandas as pd
from sqlalchemy import create_engine

logging.basicConfig(
    filename="logs/ingestion_db.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="a"
)

engine = create_engine(
    "mysql+mysqlconnector://root:091005@127.0.0.1:3306/vendor_performance_analysis",
    pool_pre_ping=True
)

def ingest_db(df, table_name, engine):
    """Ingest a DataFrame into a MySQL table."""

    try:
        logging.info(f"Starting upload of '{table_name}'")
        logging.info(f"DataFrame Shape: {df.shape}")

        start = time.time()

        with engine.begin() as conn:
            df.to_sql(
                name=table_name,
                con=conn,
                if_exists="replace",
                index=False,
                chunksize=1000,
                method="multi"
            )

        end = time.time()

        logging.info(f"'{table_name}' uploaded successfully.")
        logging.info(f"Time taken: {end-start:.2f} seconds")

    except Exception as e:
        logging.exception(f"Error while uploading '{table_name}'")
        raise


def load_raw_data():
    """Load all CSV files from the data folder into MySQL."""

    start = time.time()

    for file in os.listdir("data"):

        if file.endswith(".csv"):

            logging.info(f"Reading {file}")

            df = pd.read_csv(os.path.join("data", file))

            ingest_db(df, file[:-4], engine)

    end = time.time()

    logging.info("Raw data ingestion completed.")
    logging.info(f"Total execution time: {(end-start)/60:.2f} minutes")


if __name__ == "__main__":
    load_raw_data()
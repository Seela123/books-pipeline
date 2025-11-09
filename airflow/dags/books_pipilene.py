from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import os
from pathlib import Path
import sys

PROJ_ROOT = "/opt/ee"
CSV_PATH  = f"{PROJ_ROOT}/data/bronze/books_toscrape_raw_cleaned.csv"
SCRAPER   = f"{PROJ_ROOT}/scraping.py"
DBT_PROJ  = f"{PROJ_ROOT}/dbt/books_project"

default_args = {
    "owner": "selman",
    "retries": 2,
    "retry_delay": timedelta(minutes=2),
}

# Allow import from your project if needed
sys.path.append(f"{PROJ_ROOT}")

with DAG(
    dag_id="books_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    tags=["bronze", "silver", "gold"],
) as dag:


    scrape = BashOperator(
        task_id="scrape_books",
        bash_command=f'python "{SCRAPER}"',
    )


    def load_csv_to_bronze():
        import pandas as pd
        from sqlalchemy import create_engine
        df = pd.read_csv(CSV_PATH)

        engine = create_engine(
            f"postgresql+psycopg2://{os.getenv('PG_USER')}:{os.getenv('PG_PASSWORD')}@{os.getenv('PG_HOST')}:{os.getenv('PG_PORT')}/{os.getenv('PG_DB')}"
        )
        df.to_sql("books_toscrape", engine, schema="bronze", if_exists="replace", index=False)
        print("Bronze table updated successfully.")

    load_bronze = PythonOperator(
        task_id="load_to_bronze",
        python_callable=load_csv_to_bronze,
    )


    dbt_silver = BashOperator(
        task_id="run_dbt_silver",
        cwd=DBT_PROJ,
        bash_command='dbt run -s silver',
    )


    dbt_gold = BashOperator(
        task_id="run_dbt_gold",
        cwd=DBT_PROJ,
        bash_command='dbt run -s gold',
    )


    scrape >> load_bronze >> dbt_silver >> dbt_gold

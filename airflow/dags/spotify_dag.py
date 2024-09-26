from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

# Import function from spotify_etl.py
from spotify_etl import run_spotify_etl

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 9, 24),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

# Define the DAG
dag = DAG(
    'spotify_dag',
    default_args=default_args,
    description='Spotify ETL DAG!',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

# Function to print current working directory and database path
def print_working_directory():
    import os

    # Get path database from environment variable or default
    DATABASE_LOCATION = os.getenv("DATABASE_LOCATION", "sqlite:///my_played_tracks.sqlite")

    if DATABASE_LOCATION.startswith("sqlite:///"):
        db_file = DATABASE_LOCATION.replace("sqlite:///", "")
    else:
        db_file = DATABASE_LOCATION

    # Print current working directory and database path
    print(f"Current working directory: {os.getcwd()}")
    print(f"Database will be created at: {os.path.abspath(db_file)}")

# Define task to check path and working directory
check_path_task = PythonOperator(
    task_id='check_path',
    python_callable=print_working_directory,
    dag=dag,
)

# Define task to run Spotify ETL
run_etl = PythonOperator(
    task_id='whole_spotify_etl',
    python_callable=run_spotify_etl,
    dag=dag,
)

# Set task dependencies
check_path_task >> run_etl  # check_path_task will run before run_etl

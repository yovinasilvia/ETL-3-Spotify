# ETL Spotify Data Pipeline with Astro

## Project Overview
This project demonstrates an ETL (Extract, Transform, Load) pipeline that retrieves data from the Spotify API and stores it in an SQLite database. The pipeline tracks and analyzes your Spotify listening history, including song titles, artist names, timestamps, and play counts. The project is managed using Astro, a platform for orchestrating workflows with Apache Airflow, which simplifies the scheduling and execution of the ETL pipeline.

## Getting Started
### Clone This Repository
```
git clone https://github.com/yovinasilvia/ETL-3-Spotify.git
```
### Project Directory Setup
First, I created a project directory named ETL-3-Spotify. You can name it based on your preference.
```
mkdir ETL-3-Spotify
cd ETL-3-Spotify
```
### Create a Virtual Environment
I then created a virtual environment to manage the dependencies.
```
python -m venv .venv
.venv\Scripts\activate  # On Windows
```
### Spotify API Access
To access the Spotify API, visit [Spotify Developer Portal](https://developer.spotify.com/documentation/web-api) follow the instruction and create an app. This will provide you with the `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`.

### Obtaining API Token
To get the access token for your Spotify account, I used the following command in the VS Code terminal (Bash):
```
curl -X POST "https://accounts.spotify.com/api/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=client_credentials&client_id=<your_client_id>&client_secret=<your_client_secret>"
```
This will return an access_token. Make sure to copy it.

### Running app.py
Next, I ran the [app.py](mysong_playlist/app.py) file in the terminal to initialize the API authorization:
```
python app.py
```

### Authorizing Spotify App
To authorize the app with your account, open your browser and use the following URL, replacing `<your_client_id>` with the `SPOTIFY_CLIENT_ID` from the Spotify Developer Dashboard:
```
https://accounts.spotify.com/authorize?client_id=<your_client_id>&response_type=code&redirect_uri=http://localhost:8888/callback&scope=user-read-recently-played
```
This will generate an authorization code. Copy this code for the next step.

### Getting the `Refresh_Token`
In the terminal, run the following command to exchange the authorization code for an `access_token` and `refresh_token`:
```
curl -X POST "https://accounts.spotify.com/api/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=authorization_code&code=<your_authorization_code>&redirect_uri=http://localhost:8888/callback&client_id=<your_client_id>&client_secret=<your_client_secret>"
```
The response will look something like this:
```
{
  "access_token": "<your_access_token>",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "<your_refresh_token>",
  "scope": "user-read-recently-played"
}
```

### Storing Credentials in `.env`
Now, create a `.env` file in the project root directory and store the credentials:
```
DATABASE_LOCATION="sqlite:///dags/my_played_tracks.sqlite"
SPOTIFY_USER_ID=<your_spotify_user_id>
SPOTIFY_TOKEN=<your_access_token>
SPOTIFY_REFRESH_TOKEN=<your_refresh_token>
SPOTIFY_CLIENT_ID=<your_client_id>
SPOTIFY_CLIENT_SECRET=<your_client_secret>
```
Make sure to replace the placeholders with your actual values from the steps above.

### Initializing Airflow with Astro
Before you run the Astro CLI you need to [download](https://github.com/astronomer/astro-cli/releases) the installer and add the installer path to your local environment variables.
After setting up Spotify APIa and Astro CLI, I initialized Airflow using Astro for scheduling the ETL tasks.
* Initialize Astro in the project:
```
astro dev init
```
This will generate the necessary project structure for Airflow within Astro.

* Create a directory for Airflow configuration:

In my project, I created an airflow directory where all Airflow-related settings are stored.

* Creating `spotify_etl.py`

Create the [spotify_etl.py](airflow/dags/spotify_etl.py) file inside the `dags` directory within the `airflow` folder. This file contains the logic to extract data from Spotify, validate it, and load it into the SQLite database.

* Creating `spotify_dag.py`

Next, create the [spotify_dag.py](airflow/dags/spotify_dag.py) file in the same dags directory. This file will contain the DAG definition to schedule the ETL process using Airflow.

* Ensure Both Files are in the dags Directory

Make sure both `spotify_etl.py` and `spotify_dag.py` are inside the `dags` directory within the `airflow` folder. This is important because Airflow looks for DAG definitions in the `dags` folder.

### Setting Up Airflow
* Create a Virtual Environment for Airflow:

In the `airflow` directory, I set up a separate virtual environment for running Airflow tasks:
```
cd airflow
python -m venv airflow-venv
source airflow-venv\Scripts\activate # On Mac: airflow-venv/bin/activate 
```
* Docker Configuration:

I configured the [Dockerfile](airflow/Dockerfile) and [config.yaml](airflow/.astro/config.yaml) (these were provided in the project) to ensure that Airflow is set up correctly to run the DAG.

* Astro Airflow Start:

Once the configuration was complete, I started the Airflow instance through Astro using the command:
```
astro dev start
```

### Running the ETL Pipeline
Once Airflow is running, the ETL pipeline defined in `spotify_dag.py` will be automatically scheduled to run. The data will be fetched from Spotify, validated, and loaded into the SQLite database.

## Project Structure
Here is the updated Project Structure based on your final clarification that the `Dockerfile` is located in the `airflow/` directory:
```
ETL-3-Spotify/
│
├── mysong_playlist/           # Folder for Spotify API-related scripts and dependencies
│   ├── app.py                 # Python script for Spotify API authentication (handles tokens)
│   ├── main.py                # Python script to initialize and load environment variables
│   ├── .env                   # Environment variables for Spotify credentials (SPOTIFY_CLIENT_ID, SPOTIFY_SECRET, etc.)
│   └── requirements.txt       # Python dependencies for the Spotify API and other project needs
│
├── airflow/                   # Folder containing Airflow-related configuration, DAGs, and Docker setup
│   ├── dags/                  # DAGs folder where Airflow looks for the DAG files and ETL scripts
│   │   ├── spotify_etl.py     # Python script to handle the ETL process (extracting, transforming, and loading data)
│   │   ├── spotify_dag.py     # Python script defining the Airflow DAG to schedule the ETL
│   │   ├── .env               # Environment variables required by Airflow (SPOTIFY credentials, DB location)
│   │
│   ├── .astro/                # Folder containing Astro-specific configuration files
│   │   └── config.yaml        # Astro's configuration file for Airflow setup
│   ├── Dockerfile             # Dockerfile to set up the Airflow environment inside Astro
│   ├── airflow_settings.yaml  # Airflow-specific configuration settings
│   └── airflow-venv/          # Virtual environment specifically for Airflow
│
├── .venv/                     # Virtual environment for the main project (mysong_playlist)
├── README.md                  # Documentation for the project
```

### Breakdown of Key Components:
1. `mysong_playlist/`: Contains all scripts and dependencies related to interacting with the Spotify API:
    * `app.py`: Handles authentication and token management for the Spotify API. 
    * `main.py`: Initializes the environment by loading variables from the .env file and setting up the connection to the Spotify API.
    * `.env`: Stores the environment variables, such as SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_TOKEN, and SPOTIFY_REFRESH_TOKEN.
    * `requirements.txt`: Lists all the Python dependencies needed to work with the Spotify API and handle other project-specific requirements.

2. `airflow/`: Contains all the files necessary for Airflow and Astro to orchestrate the ETL pipeline:
    * `dags/`: This directory is where the Airflow DAG and ETL scripts are stored:
        * `spotify_etl.py`: Contains the logic to extract Spotify data, validate it, and load it into the SQLite database.
        * `spotify_dag.py`: Defines the Airflow DAG, which schedules the ETL tasks (calls spotify_etl.py).
        * `.env`: Holds environment variables required by Airflow, such as the database location and Spotify API credentials, for execution within Airflow.
    * `.astro/`: Contains Astro-specific configuration files that help set up and manage the Airflow environment:
        * `config.yaml`: Configures how Astro manages the Airflow setup.
    * `Dockerfile`: The Dockerfile used to define the environment in which Astro will run Airflow. This sets up dependencies, services, and configurations needed by Airflow.
    * `airflow_settings.yaml`: Configuration settings for running Airflow tasks.
    * `airflow-venv/`: A separate virtual environment dedicated to Airflow.

3. `.venv/`: A virtual environment dedicated to the main project (everything in mysong_playlist/), which is separate from the virtual environment used by Airflow.

### Important Notes:
1. Dockerfile in `airflow/`: The `Dockerfile` in the `airflow/` directory defines how Astro sets up the Airflow environment. This ensures that all necessary dependencies (like Flask, Pandas, etc.) are installed in the Docker container.

2. Multiple `.env` Files:
    * The `.env` file in `mysong_playlist/` is used for managing environment variables related to Spotify API interactions (e.g., client IDs, tokens).
    * The `.env` file in `airflow/dags/` is used by Airflow to ensure that the DAG can execute using the necessary credentials and database locations during ETL processing.



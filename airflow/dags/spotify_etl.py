import sqlalchemy
import pandas as pd
import requests
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load environment variables from .env file
env_file_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=env_file_path)

# Verifikasi bahwa semua variabel berhasil dimuat
print(f"DATABASE_LOCATION: {os.getenv('DATABASE_LOCATION')}")
print(f"SPOTIFY_USER_ID: {os.getenv('SPOTIFY_USER_ID')}")
print(f"SPOTIFY_TOKEN: {os.getenv('SPOTIFY_TOKEN')}")
print(f"SPOTIFY_REFRESH_TOKEN: {os.getenv('SPOTIFY_REFRESH_TOKEN')}")
print(f"SPOTIFY_CLIENT_ID: {os.getenv('SPOTIFY_CLIENT_ID')}")
print(f"SPOTIFY_CLIENT_SECRET: {os.getenv('SPOTIFY_CLIENT_SECRET')}")

# Check if the necessary environment variables are loaded
DATABASE_LOCATION = os.getenv("DATABASE_LOCATION", "sqlite:///dags/my_played_tracks.sqlite")
USER_ID = os.getenv("SPOTIFY_USER_ID")
TOKEN = os.getenv("SPOTIFY_TOKEN")
REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

if not all([DATABASE_LOCATION, USER_ID, TOKEN, REFRESH_TOKEN, CLIENT_ID, CLIENT_SECRET]):
    raise ValueError("Environment variables for database or Spotify API are missing. Please check your .env file.")

def refresh_access_token():
    """
    Refreshes the Spotify access token using the refresh token.
    """
    global TOKEN  # Make sure TOKEN is updated globally
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code != 200:
        raise Exception("Could not refresh access token. Please check your refresh token and client credentials.")
    
    response_json = response.json()
    TOKEN = response_json["access_token"]
    print(f"New TOKEN: {TOKEN}")  # Print new token for verification
    return TOKEN

def check_if_valid_data(df: pd.DataFrame) -> bool:
    # Check if dataframe is empty
    if df.empty:
        print("No songs downloaded. Finishing execution")
        return False 

    # Primary Key Check
    if pd.Series(df['played_at']).is_unique:
        pass
    else:
        raise Exception("Primary Key check is violated")

    # Check for nulls
    if df.isnull().values.any():
        raise Exception("Null values found")

    # Check that all timestamps are within the last 60 days
    today = datetime.now().date()
    start_date = today - timedelta(days=60)

    timestamps = df["timestamp"].tolist()
    for timestamp in timestamps:
        ts_date = datetime.strptime(timestamp, '%Y-%m-%d').date()
        if not (start_date <= ts_date <= today):
            raise Exception(f"At least one of the returned songs does not have a timestamp within the last 60 days: {timestamp}")

    return True

def create_table_with_play_count(engine):
    """
    Create table with play_count column if it does not exist using SQLAlchemy.
    """
    with engine.connect() as connection:
        sql_query = """
        CREATE TABLE IF NOT EXISTS my_played_tracks(
            song_name VARCHAR(200),
            artist_name VARCHAR(200),
            played_at VARCHAR(200),
            timestamp VARCHAR(200),
            play_count INTEGER DEFAULT 1,
            CONSTRAINT primary_key_constraint PRIMARY KEY (played_at)
        )
        """
        connection.execute(sql_query)
        print("Table created with 'play_count' column.")

def update_play_count(engine, song_name, artist_name):
    """
    Update play count for each song in the database using SQLAlchemy.
    """
    with engine.connect() as connection:
        update_query = """
        UPDATE my_played_tracks
        SET play_count = play_count + 1
        WHERE song_name = :song_name AND artist_name = :artist_name
        """
        connection.execute(update_query, {'song_name': song_name, 'artist_name': artist_name})

def run_spotify_etl():
    global TOKEN  # Use the global TOKEN
    # Extract part of the ETL process
    headers = {
        "Accept" : "application/json",
        "Content-Type" : "application/json",
        "Authorization" : f"Bearer {TOKEN}"  # Use the global TOKEN
    }
    
    # Convert time to Unix timestamp in milliseconds
    today = datetime.now()
    start_date = today - timedelta(days=60)
    start_unix_timestamp = int(start_date.timestamp()) * 1000

    # Download all songs you've listened to "after yesterday", which means in the last 24 hours      
    r = requests.get(f"https://api.spotify.com/v1/me/player/recently-played?after={start_unix_timestamp}", headers=headers)

    # If the token is expired, refresh it
    if r.status_code == 401:  # Unauthorized error
        print("Access token expired. Refreshing token...")
        TOKEN = refresh_access_token()  # Refresh and update TOKEN
        headers["Authorization"] = f"Bearer {TOKEN}"
        r = requests.get(f"https://api.spotify.com/v1/me/player/recently-played?after={start_unix_timestamp}", headers=headers)

    if r.status_code != 200:
        raise Exception(f"Failed to retrieve data from Spotify API. Status code: {r.status_code}")

    data = r.json()

    song_names = []
    artist_names = []
    played_at_list = []
    timestamps = []

    # Extracting only the relevant bits of data from the json object      
    for song in data["items"]:
        song_names.append(song["track"]["name"])
        artist_names.append(song["track"]["album"]["artists"][0]["name"])
        played_at_list.append(song["played_at"])
        timestamps.append(song["played_at"][0:10])
        
    # Prepare a dictionary in order to turn it into a pandas dataframe below       
    song_dict = {
        "song_name" : song_names,
        "artist_name": artist_names,
        "played_at" : played_at_list,
        "timestamp" : timestamps
    }

    song_df = pd.DataFrame(song_dict, columns = ["song_name", "artist_name", "played_at", "timestamp"])
    
    # Validate
    if check_if_valid_data(song_df):
        print("Data valid, proceed to Load stage")

    # Load

    # Connect to database using SQLAlchemy
    engine = sqlalchemy.create_engine(DATABASE_LOCATION)

    # Create table with 'play_count' column if it does not exist
    create_table_with_play_count(engine)

    # Process each row in the DataFrame
    for index, row in song_df.iterrows():
        # Check if song already exists in the database
        query = """
        SELECT * FROM my_played_tracks WHERE song_name = :song_name AND artist_name = :artist_name
        """
        with engine.connect() as connection:
            result = connection.execute(sqlalchemy.text(query), {'song_name': row['song_name'], 'artist_name': row['artist_name']}).fetchone()
        
        if result:
            # If song exists, update play_count
            update_play_count(engine, row['song_name'], row['artist_name'])
        else:
            # If song does not exist, insert it
            song_df.loc[[index]].to_sql("my_played_tracks", con=engine, index=False, if_exists='append')

    print("Data loaded into the database successfully")

# backend/core/room_monitor.py
import pandas as pd
import datetime

def load_usage_data(path="backend/db/courses_data.csv"):
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df

def get_current_empty_rooms(df):
    now = datetime.datetime.now().time()
    current_df = df[df["time_start"] <= str(now)]
    current_df = current_df[current_df["time_end"] >= str(now)]
    empty_rooms = df["room"].unique().tolist()
    used_rooms = current_df["room"].unique().tolist()
    return [r for r in empty_rooms if r not in used_rooms]

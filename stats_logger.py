import os
import csv
import json
import time
from threading import Lock

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

locks = {}

def _get_lock(stream_id):
    if stream_id not in locks:
        locks[stream_id] = Lock()
    return locks[stream_id]

def cleaner():
    FILE_PATH = "logs/stats.csv"
    DAYS_TO_KEEP = 7  # change this

    cutoff_timestamp = int(time.time() - DAYS_TO_KEEP * 86400)

    rows_to_keep = []

    with open(FILE_PATH, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            
            try:
                if int(row["timestamp"]) >= cutoff_timestamp:

                    rows_to_keep.append(row)
                    
            except (KeyError, ValueError):
                # skip malformed rows
                pass

    # Rewrite file with filtered data
    with open(FILE_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_to_keep)
    

def log_stats(stream_id, stats):
    try:
        cleaner()
        a =1 
    except Exception as e:
        print(e)

    try:
        ts = int(time.time())
        last_frame_age = ts - int(stats["last_frame"])
        if last_frame_age > 30:
            last_frame_age = 30
        else:
            None

        row = {
            "timestamp": ts,
            "stream_id": stream_id,
            "last_frame_age": (
                last_frame_age
                if stats.get("last_frame")
                else None
            )
        }

        lock = _get_lock(stream_id)

        # ---- CSV ----
        csv_path = f"logs/stats.csv"
        write_header = not os.path.exists(csv_path)

        with lock, open(csv_path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=row.keys())
            if write_header:
                writer.writeheader()
            writer.writerow(row)


    except Exception as e:
        print("Stats logging error:", e)

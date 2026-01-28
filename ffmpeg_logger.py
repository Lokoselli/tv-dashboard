import os
import time

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def log_ffmpeg(stream_id, line):
    try:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        path = f"{LOG_DIR}/ffmpeg_stream_{stream_id}.log"

        with open(path, "a") as f:
            f.write(f"[{ts}] {line}")

    except Exception as e:
        print("FFmpeg log write error:", e)

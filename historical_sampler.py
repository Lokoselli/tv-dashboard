import time
from stream_monitor import stream_stats
from stats_logger import log_stats

LOG_INTERVAL = 10  # seconds

def sampler_loop():
    while True:
        try:
            for stream_id, stats in stream_stats.items():
                log_stats(stream_id, stats)
        except Exception as e:
            print("Sampler error:", e)

        time.sleep(LOG_INTERVAL)

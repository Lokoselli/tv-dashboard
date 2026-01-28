import subprocess
import threading
import time
from ffmpeg_logger import log_ffmpeg


RESTART_DELAY = 15  # seconds

stream_stats = {}
processes = {}

def monitor_stream(stream_id, udp_url):
    while True:
        try:
            cmd = [
                "ffmpeg",
                "-loglevel", "info",
                "-stats",
                "-i", udp_url,
                "-f", "null",
                "-"
            ]

            proc = subprocess.Popen(
                cmd,
                stderr=subprocess.PIPE,
                text=True
            )

            processes[stream_id] = proc

            stream_stats[stream_id] = {
                "status": "running",
                "last_frame": time.time(),
                "errors": 0,
                "frozen": False,
                "bitrate_kbps": 0,
                "packet_loss": 0,
                "pid": proc.pid
            }

            # READ STDERR UNTIL PROCESS EXITS
            for line in proc.stderr:
                now = time.time()
    
                if "frame=" in line:
                    stream_stats[stream_id]["last_frame"] = now

                if "bitrate=" in line:
                    try:
                        br = line.split("bitrate=")[1].split("kbits")[0]
                        stream_stats[stream_id]["bitrate_kbps"] = float(br.strip())
                    except:
                        pass

                if "missed" in line.lower() or "overrun" in line.lower():
                    stream_stats[stream_id]["packet_loss"] += 1

                frozen = (now - stream_stats[stream_id]["last_frame"]) > 6
                stream_stats[stream_id]["frozen"] = frozen
                stream_stats[stream_id]["status"] = "frozen" if frozen else "running"

            # 🔴 IF WE GET HERE, FFMPEG EXITED
            stream_stats[stream_id]["status"] = "dead"

        except Exception as e:
            stream_stats[stream_id] = {
                "status": "error",
                "message": str(e)
            }

        # ⏳ CONTROLLED RESTART (NO STORM)
        time.sleep(RESTART_DELAY)

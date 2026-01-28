import subprocess
import os

players = {}

def start_player(stream_id, udp_url):
    try:
        if stream_id in players:
            return

        os.makedirs("hls", exist_ok=True)

        cmd = [
            "ffmpeg",
            "-loglevel", "warning",
            "-stats",
            "-i", udp_url,

            "-c:v", "copy",
            "-c:a", "copy",

            "-f", "hls",
            "-hls_time", "2",
            "-hls_list_size", "5",

            "-hls_flags", "delete_segments+program_date_time",
            "-hls_delete_threshold", "2",

            f"hls/{stream_id}.m3u8"
        ]

        players[stream_id] = subprocess.Popen(
            cmd,
            stderr=subprocess.PIPE,
            text=True
        )

    except Exception as e:
        print("HLS start error:", e)

def stop_player(stream_id):
    try:
        if stream_id in players:
            players[stream_id].terminate()
            del players[stream_id]
    except Exception as e:
        print("Player stop error:", e)

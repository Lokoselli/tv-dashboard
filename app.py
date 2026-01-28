from flask import Flask, jsonify, request, send_from_directory,send_file
import csv
import threading
from stream_monitor import monitor_stream, stream_stats
from stream_player import start_player, stop_player
import threading
from historical_sampler import sampler_loop
import pandas as pd
import os


app = Flask(__name__)

streams = []



threading.Thread(
    target=sampler_loop,
    daemon=True
).start()

# Load CSV
with open("streams.csv") as f:
    reader = csv.DictReader(f)
    streams = list(reader)

# Start monitors
for s in streams:
    threading.Thread(
        target=monitor_stream,
        args=(s["id"], s["udp_url"]),
        daemon=True
    ).start()


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "logs", "stats.csv")

@app.route("/stats.csv")
def stats():
    return send_file(CSV_PATH, mimetype="text/csv")



@app.route("/api/streams")
def get_streams():
    return jsonify(streams)

@app.route("/api/status")
def status():
    return jsonify(stream_stats)

@app.route("/api/play/<stream_id>")
def play(stream_id):
    try:
        stream = next(s for s in streams if s["id"] == stream_id)
        start_player(stream_id, stream["udp_url"])
        return jsonify({"status": "playing"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/stop/<stream_id>")
def stop(stream_id):
    stop_player(stream_id)
    return jsonify({"status": "stopped"})

@app.route("/hls/<path:path>")
def hls(path):
    return send_from_directory("hls", path)

@app.route("/")
def home():
    return send_from_directory("static", "data.html")

app.run(host="0.0.0.0", port=5000)

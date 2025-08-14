import os
import subprocess
from threading import Thread
from flask import Flask

# -----------------------------
# PART 1: Discord Bot Launcher
# -----------------------------
folder_path = "code"
processes = []

def start_bots():
    for filename in os.listdir(folder_path):
        if filename.endswith(".py"):
            file_path = os.path.join(folder_path, filename)
            print(f"Starting {filename}...")
            p = subprocess.Popen(["python3", file_path])
            processes.append(p)

# Optional: auto-restart bots if they crash
def monitor_bots():
    while True:
        for i, p in enumerate(processes):
            if p.poll() is not None:  # process has exited
                print(f"{folder_path}/{os.listdir(folder_path)[i]} crashed. Restarting...")
                new_p = subprocess.Popen(["python3", os.path.join(folder_path, os.listdir(folder_path)[i])])
                processes[i] = new_p

# Start bots in a separate thread
Thread(target=start_bots).start()
Thread(target=monitor_bots, daemon=True).start()

# -----------------------------
# PART 2: Simple Flask Web App
# -----------------------------
app = Flask(__name__)

@app.route("/")
def home():
    return "Hey! Your bots are alive 😎"

# Render sets the port via environment variable
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)

"""
Launches the backend, frontend, and an ngrok tunnel together, then prints
the public HTTPS URL for sharing.

Requirements:
- ngrok installed and available on PATH (https://ngrok.com/download), and
  authenticated at least once via `ngrok config add-authtoken <token>`.
- Backend dependencies installed (see backend/) and frontend dependencies
  installed (`npm install` inside frontend/).

Usage:
    python public.py
"""

import atexit
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
FRONTEND_PORT = 3000
NGROK_API_URL = "http://127.0.0.1:4040/api/tunnels"

processes = []


def start_process(command, cwd, name):
    print(f"Starting {name}...")
    process = subprocess.Popen(
        command,
        cwd=cwd,
        shell=(os.name == "nt"),
    )
    processes.append((name, process))
    return process


def stop_all():
    for name, process in processes:
        if process.poll() is None:
            print(f"Stopping {name}...")
            process.terminate()


def fetch_public_url(retries=20, delay=1.0):
    for _ in range(retries):
        try:
            with urllib.request.urlopen(NGROK_API_URL, timeout=2) as response:
                data = json.load(response)
                for tunnel in data.get("tunnels", []):
                    if tunnel.get("proto") == "https":
                        return tunnel.get("public_url")
        except (urllib.error.URLError, ConnectionError):
            pass
        time.sleep(delay)
    return None


def main():
    atexit.register(stop_all)

    start_process([sys.executable, "app.py"], BACKEND_DIR, "backend (Flask)")
    time.sleep(2)

    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    start_process([npm_cmd, "run", "dev"], FRONTEND_DIR, "frontend (Vite)")
    time.sleep(3)

    start_process(
        ["ngrok", "http", str(FRONTEND_PORT)],
        ROOT_DIR,
        "ngrok tunnel",
    )

    print("Waiting for ngrok tunnel to come up...")
    public_url = fetch_public_url()

    if public_url:
        print("\n" + "=" * 60)
        print(f"  Public URL: {public_url}")
        print("=" * 60 + "\n")
    else:
        print(
            "Could not fetch the public URL from the ngrok API. "
            "Check that ngrok is installed and on PATH, and that it "
            "started successfully."
        )

    try:
        while True:
            time.sleep(1)
            for name, process in processes:
                if process.poll() is not None:
                    print(f"{name} exited unexpectedly.")
                    return
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()

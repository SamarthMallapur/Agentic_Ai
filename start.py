"""
Placement Readiness Companion - All-in-One Runner
Starts both the FastAPI backend and React frontend with a single command.

Usage:
    python start.py
    python start.py --no-browser
"""

import os
import sys
import time
import shutil
import signal
import socket
import threading
import subprocess
import webbrowser
from pathlib import Path

# Paths
ROOT_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT_DIR / "frontend"
DB_FILE = ROOT_DIR / "placement.db"
ENV_FILE = ROOT_DIR / ".env"
ENV_EXAMPLE = ROOT_DIR / ".env.example"

# ANSI Colors
CYAN = "\033[96m"
MAGENTA = "\033[95m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

running_processes = []
shutting_down = False


def log(prefix: str, color: str, message: str):
    print(f"{color}{BOLD}[{prefix:8}]{RESET} {message}", flush=True)


def stream_output(proc: subprocess.Popen, prefix: str, color: str):
    """Streams process stdout/stderr line by line with formatted prefix."""
    try:
        for line in iter(proc.stdout.readline, b""):
            if shutting_down:
                break
            text = line.decode("utf-8", errors="replace").rstrip()
            if text:
                print(f"{color}{BOLD}[{prefix:8}]{RESET} {text}", flush=True)
    except (ValueError, IOError):
        pass


def is_port_in_use(port: int) -> bool:
    """Checks if a local TCP port is already open."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0


def wait_for_port(port: int, timeout: float = 12.0) -> bool:
    """Waits until a local port is open and accepting connections."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        if is_port_in_use(port):
            return True
        time.sleep(0.3)
    return False


def setup_environment():
    """Validates prerequisites, sets up .env, database, and npm dependencies."""
    print("=" * 65, flush=True)
    print(f"{GREEN}{BOLD} Placement Readiness Companion - Runner{RESET}", flush=True)
    print("=" * 65, flush=True)

    # 1. Check/copy .env
    if not ENV_FILE.exists():
        if ENV_EXAMPLE.exists():
            log("SETUP", YELLOW, "Copying .env.example to .env...")
            shutil.copy(ENV_EXAMPLE, ENV_FILE)
            log("SETUP", YELLOW, "Please configure your GEMINI_API_KEY in .env if needed.")
        else:
            log("SETUP", RED, "Warning: .env file missing.")

    # 2. Check and initialize database
    if not DB_FILE.exists():
        log("SETUP", YELLOW, "Database not found. Initializing database and seed data...")
        try:
            subprocess.run([sys.executable, str(ROOT_DIR / "database" / "models.py")], check=True)
            subprocess.run([sys.executable, str(ROOT_DIR / "data" / "seed_data" / "seed.py")], check=True)
            subprocess.run([sys.executable, str(ROOT_DIR / "scripts" / "ingest_jobs.py")], check=True)
            log("SETUP", GREEN, "Database and seed data initialized successfully.")
        except subprocess.CalledProcessError as e:
            log("SETUP", RED, f"Failed to initialize database: {e}")
            sys.exit(1)

    # 3. Check npm
    npm_cmd = shutil.which("npm.cmd") if os.name == "nt" else shutil.which("npm")
    if not npm_cmd:
        log("SETUP", RED, "Error: 'npm' was not found in PATH. Please install Node.js.")
        sys.exit(1)

    # 4. Check frontend node_modules
    if not (FRONTEND_DIR / "node_modules").exists():
        log("SETUP", YELLOW, "Frontend dependencies missing. Running 'npm install'...")
        try:
            cmd = ["cmd.exe", "/c", "npm", "install"] if os.name == "nt" else ["npm", "install"]
            subprocess.run(cmd, cwd=FRONTEND_DIR, check=True)
            log("SETUP", GREEN, "Frontend dependencies installed successfully.")
        except subprocess.CalledProcessError as e:
            log("SETUP", RED, f"Failed to run npm install: {e}")
            sys.exit(1)

    return npm_cmd


def kill_proc(proc: subprocess.Popen):
    """Terminates process and all its children across Windows/Linux."""
    if proc.poll() is not None:
        return
    try:
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        else:
            proc.terminate()
            proc.wait(timeout=3)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def cleanup(signum=None, frame=None):
    """Signal handler for graceful shutdown."""
    global shutting_down
    if shutting_down:
        return
    shutting_down = True
    print("\n" + "=" * 65, flush=True)
    log("SHUTDOWN", YELLOW, "Stopping all services...")
    for proc in running_processes:
        kill_proc(proc)
    log("SHUTDOWN", GREEN, "All services stopped. Goodbye!")
    print("=" * 65, flush=True)
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    npm_cmd = setup_environment()

    # Warn if ports are in use
    if is_port_in_use(8000):
        log("WARN", YELLOW, "Port 8000 is currently occupied. Backend may fail to bind.")
    if is_port_in_use(5173):
        log("WARN", YELLOW, "Port 5173 is currently occupied. Frontend may bind to 5174+.")

    # Start FastAPI Backend
    log("RUNNER", GREEN, "Starting FastAPI Backend on http://localhost:8000...")
    backend_proc = subprocess.Popen(
        [sys.executable, "api.py"],
        cwd=ROOT_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    running_processes.append(backend_proc)

    backend_thread = threading.Thread(
        target=stream_output,
        args=(backend_proc, "BACKEND", CYAN),
        daemon=True,
    )
    backend_thread.start()

    # Start React Frontend
    log("RUNNER", GREEN, "Starting React Frontend (Vite)...")
    frontend_cmd = ["cmd.exe", "/c", "npm", "run", "dev"] if os.name == "nt" else ["npm", "run", "dev"]
    frontend_proc = subprocess.Popen(
        frontend_cmd,
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    running_processes.append(frontend_proc)

    frontend_thread = threading.Thread(
        target=stream_output,
        args=(frontend_proc, "FRONTEND", MAGENTA),
        daemon=True,
    )
    frontend_thread.start()

    # Wait for services to be ready
    backend_ready = wait_for_port(8000, timeout=10.0)
    frontend_ready = wait_for_port(5173, timeout=10.0)

    print("-" * 65, flush=True)
    if backend_ready:
        log("READY", GREEN, "Backend API is live:    http://localhost:8000")
        log("READY", GREEN, "Interactive API Docs:   http://localhost:8000/docs")
    if frontend_ready:
        log("READY", GREEN, "Frontend App is live:   http://localhost:5173")
    print("-" * 65, flush=True)
    log("INFO", YELLOW, "Press Ctrl+C at any time to stop both servers.")
    print("-" * 65, flush=True)

    # Open browser automatically if not disabled
    if "--no-browser" not in sys.argv:
        time.sleep(1.0)
        webbrowser.open("http://localhost:5173")

    # Monitor child processes
    try:
        while True:
            if backend_proc.poll() is not None:
                log("BACKEND", RED, f"Backend process exited with code {backend_proc.returncode}")
                break
            if frontend_proc.poll() is not None:
                log("FRONTEND", RED, f"Frontend process exited with code {frontend_proc.returncode}")
                break
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        cleanup()


if __name__ == "__main__":
    main()

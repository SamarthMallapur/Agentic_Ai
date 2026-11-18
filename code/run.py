"""Start the Placement Readiness Companion.

    python run.py              start the app and open the browser
    python run.py --reset      rebuild the database and demo data, then start
    python run.py --no-browser start without opening a browser
"""
import argparse
import importlib.util
import socket
import sys
import threading
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
REQUIRED = {"fastapi": "fastapi", "uvicorn": "uvicorn", "multipart": "python-multipart", "dotenv": "python-dotenv",
            "google.genai": "google-genai", "mcp": "mcp", "pypdf": "pypdf", "docx": "python-docx"}


def free_port(start: int) -> int:
    for port in range(start, start + 20):
        with socket.socket() as sock:
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise SystemExit("No free port was found.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Placement Readiness Companion")
    parser.add_argument("--reset", action="store_true", help="delete saved data and rebuild the demo")
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    if sys.version_info < (3, 10):
        raise SystemExit("Python 3.10 or newer is required.")
    missing = [pkg for module, pkg in REQUIRED.items() if importlib.util.find_spec(module) is None]
    if missing:
        raise SystemExit(f"Missing packages: {', '.join(missing)}\nRun: python -m pip install -r requirements.txt")

    import uvicorn

    from app import config, datasets, llm

    if not (config.WEB_DIR / "index.html").exists():
        raise SystemExit("The web app build is missing. Run: cd frontend && npm install && npm run build")

    datasets.setup(reset=args.reset)
    port = free_port(args.port)
    url = f"http://127.0.0.1:{port}"
    print(f"\n  Placement Readiness Companion is running at {url}")
    print(f"  AI features: {'ON (' + config.PRIMARY_MODEL + ')' if llm.available() else 'OFF. Add GEMINI_API_KEY to code/.env to turn them on.'}")
    print("  Press Ctrl+C to stop.\n")
    if not args.no_browser:
        threading.Thread(target=lambda: (time.sleep(1.5), webbrowser.open(url)), daemon=True).start()
    uvicorn.run("app.api:app", host="127.0.0.1", port=port, log_level="warning")


if __name__ == "__main__":
    main()

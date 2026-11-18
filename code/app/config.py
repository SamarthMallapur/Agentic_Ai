"""Paths and settings. Everything configurable lives here or in .env."""
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"  # Drop Kaggle CSV files here.
DEMO_POSTINGS = DATA_DIR / "demo_postings.csv"
DEMO_RESUMES = DATA_DIR / "demo_resumes"
DEMO_JDS = DATA_DIR / "demo_jds"
WEB_DIR = ROOT / "web"  # Built React app, served by FastAPI.
SKILL_FILE = ROOT / "skills" / "resume_jd_review" / "SKILL.md"
MCP_SERVER = ROOT / "connector" / "mcp_server.py"

PRIMARY_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "gemini-3.8-flash")

# Research loop: keep widening the search until this many postings are found.
MIN_RESEARCH_SAMPLE = 30
# Sample sizes that decide a market claim's confidence label.
HIGH_CONFIDENCE_SAMPLE = 100
MEDIUM_CONFIDENCE_SAMPLE = 30
MIN_SUPPORTING_POSTINGS = 5
STALE_AFTER_DAYS = 365


def db_path() -> Path:
    return Path(os.getenv("PRC_DB", ROOT / "placement.db"))


def prompt_log_path() -> Path:
    return Path(os.getenv("PRC_PROMPT_LOG", ROOT / "logs" / "prompt_log.jsonl"))


def api_key() -> str:
    if os.getenv("PRC_OFFLINE") == "1":
        return ""
    key = os.getenv("GEMINI_API_KEY", "").strip()
    return "" if not key or key.startswith("your_") else key

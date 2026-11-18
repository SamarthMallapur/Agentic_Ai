"""SQLite storage. This schema is the project's memory schema."""
import json
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime

from . import config

SCHEMA = """
-- LONG-TERM MEMORY: one student's profile (skills, target roles, resume).
CREATE TABLE IF NOT EXISTS profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    data TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- SESSION STATE: today's application and last review, as key/value pairs.
CREATE TABLE IF NOT EXISTS session_state (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- RETRIEVAL STORE: past advice the student accepted or rejected.
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    suggestion TEXT NOT NULL,
    skill TEXT DEFAULT '',
    decision TEXT NOT NULL CHECK (decision IN ('accepted', 'rejected')),
    reason TEXT DEFAULT '',
    context TEXT DEFAULT '',
    created_at TEXT NOT NULL
);

-- APPLICATION TRACKING STORE (also exposed through the MCP connector).
CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    job_description TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'SAVED',
    applied_on TEXT,
    follow_up_on TEXT,
    resume_score INTEGER,
    notes TEXT DEFAULT '',
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS application_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    from_status TEXT,
    to_status TEXT NOT NULL,
    at TEXT NOT NULL
);

-- JOB POSTINGS: the evidence base for every market claim.
CREATE TABLE IF NOT EXISTS postings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    company TEXT DEFAULT '',
    location TEXT DEFAULT '',
    description TEXT NOT NULL,
    skills TEXT DEFAULT '',
    posted_on TEXT,
    source TEXT NOT NULL,
    source_row INTEGER NOT NULL,
    is_demo INTEGER NOT NULL DEFAULT 0
);

-- HISTORY used by the weekly report.
CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER REFERENCES applications(id) ON DELETE SET NULL,
    company TEXT DEFAULT '',
    role TEXT DEFAULT '',
    score INTEGER NOT NULL,
    confidence TEXT NOT NULL,
    result TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS interview_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER REFERENCES applications(id) ON DELETE SET NULL,
    category TEXT NOT NULL,
    skill TEXT DEFAULT '',
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    score REAL NOT NULL,
    method TEXT NOT NULL,
    confidence TEXT NOT NULL,
    feedback TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    markdown TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def today() -> date:
    return date.today()


@contextmanager
def connect():
    path = config.db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=15)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with connect() as conn:
        conn.executescript(SCHEMA)


def query(sql: str, params: tuple = ()) -> list[dict]:
    with connect() as conn:
        return [dict(row) for row in conn.execute(sql, params).fetchall()]


def execute(sql: str, params: tuple = ()) -> int:
    with connect() as conn:
        return conn.execute(sql, params).lastrowid


def set_state(key: str, value) -> None:
    execute(
        "INSERT INTO session_state (key, value, updated_at) VALUES (?, ?, ?) "
        "ON CONFLICT(key) DO UPDATE SET value = excluded.value, updated_at = excluded.updated_at",
        (key, json.dumps(value), now()),
    )


def get_state(key: str, default=None):
    rows = query("SELECT value FROM session_state WHERE key = ?", (key,))
    return json.loads(rows[0]["value"]) if rows else default

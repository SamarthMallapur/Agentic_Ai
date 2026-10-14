import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'placement.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Profile memory
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_data TEXT NOT NULL
        )
    ''')

    # Session memory
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS session (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_data TEXT NOT NULL
        )
    ''')

    # Feedback memory
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            suggestion TEXT,
            status TEXT,
            reason TEXT,
            context TEXT
        )
    ''')

    # Applications
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            role TEXT,
            job_description TEXT,
            application_date TEXT,
            source TEXT,
            status TEXT,
            resume_version TEXT,
            resume_score INTEGER,
            interview_date TEXT,
            interview_stage TEXT,
            result TEXT,
            notes TEXT,
            follow_up_date TEXT
        )
    ''')

    # Jobs (Market Data)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            location TEXT,
            description TEXT,
            skills TEXT,
            source TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()

import json
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'placement.db')

class SessionMemory:
    def __init__(self):
        self.db_path = DB_PATH
        
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_session(self) -> dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT session_data FROM session ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            return json.loads(row['session_data'])
        return {}

    def update_session(self, session_data: dict):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM session")
        cursor.execute("INSERT INTO session (session_data) VALUES (?)", (json.dumps(session_data),))
        conn.commit()
        conn.close()

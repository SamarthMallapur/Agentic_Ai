import json
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'placement.db')

class ProfileMemory:
    def __init__(self):
        self.db_path = DB_PATH
        
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_profile(self) -> dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT profile_data FROM profile ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        if row:
            return json.loads(row['profile_data'])
        return {}

    def update_profile(self, profile_data: dict):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM profile")
        cursor.execute("INSERT INTO profile (profile_data) VALUES (?)", (json.dumps(profile_data),))
        conn.commit()
        conn.close()

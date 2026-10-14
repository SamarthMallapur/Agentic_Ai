import sqlite3
import os
from typing import List, Dict

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'placement.db')

class ApplicationTracker:
    def __init__(self):
        self.db_path = DB_PATH
        
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_applications(self) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM applications ORDER BY application_date DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def add_application(self, app_data: dict) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        columns = ', '.join(app_data.keys())
        placeholders = ', '.join('?' * len(app_data))
        sql = f"INSERT INTO applications ({columns}) VALUES ({placeholders})"
        cursor.execute(sql, tuple(app_data.values()))
        conn.commit()
        last_id = cursor.lastrowid
        conn.close()
        return last_id

    def update_application_status(self, app_id: int, new_status: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE applications SET status = ? WHERE id = ?", (new_status, app_id))
        conn.commit()
        conn.close()

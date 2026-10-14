import sqlite3
import os
from typing import List, Dict

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'placement.db')

class FeedbackMemory:
    def __init__(self):
        self.db_path = DB_PATH
        
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def add_feedback(self, suggestion: str, status: str, reason: str, context: str):
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO feedback (suggestion, status, reason, context) VALUES (?, ?, ?, ?)",
            (suggestion, status, reason, context)
        )
        conn.commit()
        conn.close()

    def get_all_feedback(self) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, suggestion, status, reason, context FROM feedback")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
        
    def get_rejected_feedback(self) -> List[Dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT suggestion, reason FROM feedback WHERE status='rejected'")
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

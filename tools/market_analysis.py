import sqlite3
import os
from collections import Counter
from typing import Dict, List, Tuple

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'placement.db')

class MarketAnalysis:
    def __init__(self):
        self.db_path = DB_PATH
        
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_market_statistics(self) -> Dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT skills, title FROM jobs")
        rows = cursor.fetchall()
        conn.close()
        
        all_skills = []
        titles = []
        total_jobs = len(rows)
        
        for row in rows:
            if row['skills']:
                all_skills.extend([s.strip() for s in row['skills'].split(',')])
            if row['title']:
                titles.append(row['title'].strip())
                
        skill_counts = Counter(all_skills)
        title_counts = Counter(titles)
        
        # Calculate percentages
        skill_demand = {skill: round((count / total_jobs) * 100) for skill, count in skill_counts.items()}
        
        return {
            "total_jobs_analyzed": total_jobs,
            "top_skills": skill_counts.most_common(10),
            "skill_demand_percentage": skill_demand,
            "common_roles": title_counts.most_common(5)
        }

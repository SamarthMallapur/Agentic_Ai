import csv
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'placement.db')
CSV_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'sample_jobs.csv')

def normalize_skill(skill: str) -> str:
    skill = skill.strip().lower()
    mapping = {
        "react.js": "react",
        "reactjs": "react",
        "node.js": "node.js",
        "nodejs": "node.js",
        "postgres": "postgresql",
        "c plus plus": "c++"
    }
    return mapping.get(skill, skill.title() if len(skill) > 3 else skill.upper())

def ingest_jobs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # clear existing for demo purposes
    cursor.execute('DELETE FROM jobs')

    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            skills = row.get('skills', '').split('|')
            normalized_skills = [normalize_skill(s) for s in skills if s.strip()]
            
            cursor.execute('''
                INSERT INTO jobs (title, company, location, description, skills, source)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (row['title'], row['company'], row['location'], row['description'], ",".join(normalized_skills), row['source']))
    
    conn.commit()
    conn.close()
    print("Jobs ingested successfully.")

if __name__ == "__main__":
    ingest_jobs()

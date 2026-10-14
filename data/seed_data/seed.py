import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'placement.db')

def seed_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Seed Profile
    profile_data = {
        "name": "Jane Doe",
        "education": "B.Tech in Computer Science",
        "cgpa": 8.5,
        "graduation_year": 2027,
        "target_roles": ["Software Engineer", "Backend Developer"],
        "preferred_industries": ["Technology", "Finance"],
        "preferred_locations": ["Bangalore", "Hyderabad"],
        "technical_skills": ["C++", "Python", "SQL", "React", "Git", "DSA"],
        "soft_skills": ["Communication", "Teamwork"],
        "projects": ["AI Resume Analyzer", "OCR Pipeline", "Full Stack Application"],
        "internships": ["Summer Intern at TechCorp"],
        "certifications": ["AWS Certified Cloud Practitioner"],
        "current_resume": "Jane_Doe_Resume.pdf",
        "career_goals": "To become a backend systems engineer at a top tech company.",
        "weak_areas": ["System Design", "Docker"],
        "interview_history": ["TechCorp - Technical Round - Good feedback on DSA"],
        "accepted_feedback": ["Added more details to OCR pipeline project"],
        "rejected_feedback": ["Add advanced Kubernetes (Never used it)"]
    }
    cursor.execute('DELETE FROM profile')
    cursor.execute('INSERT INTO profile (profile_data) VALUES (?)', (json.dumps(profile_data),))

    # Seed Feedback
    cursor.execute('DELETE FROM feedback')
    feedbacks = [
        ("Add Docker to skills", "rejected", "Student has never used Docker", "resume_v1"),
        ("Highlight API development in OCR project", "accepted", "Makes project look more complete", "resume_v2")
    ]
    for fb in feedbacks:
        cursor.execute('INSERT INTO feedback (suggestion, status, reason, context) VALUES (?, ?, ?, ?)', fb)

    # Seed Applications
    cursor.execute('DELETE FROM applications')
    apps = [
        ("Example Corp", "Software Engineer", "We are looking for a backend engineer...", "2026-09-01", "LinkedIn", "APPLIED", "resume_v3", 85, None, "", "", "Good match", None),
        ("TechInnovate", "Backend Developer", "Strong Python and SQL required...", "2026-08-20", "Company Site", "INTERVIEW", "resume_v2", 78, "2026-09-15", "Technical", "", "Need to brush up on SQL", "2026-09-16")
    ]
    for app in apps:
        cursor.execute('''INSERT INTO applications 
            (company, role, job_description, application_date, source, status, resume_version, resume_score, interview_date, interview_stage, result, notes, follow_up_date) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', app)

    conn.commit()
    conn.close()
    print("Database seeded successfully.")

if __name__ == "__main__":
    seed_database()

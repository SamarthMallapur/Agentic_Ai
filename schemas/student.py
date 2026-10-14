from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class StudentProfile(BaseModel):
    name: str
    education: str
    cgpa: float
    graduation_year: int
    target_roles: List[str]
    preferred_industries: List[str]
    preferred_locations: List[str]
    technical_skills: List[str]
    soft_skills: List[str]
    projects: List[str]
    internships: List[str]
    certifications: List[str]
    current_resume: str = ""
    career_goals: str = ""
    weak_areas: List[str] = []
    interview_history: List[str] = []
    accepted_feedback: List[str] = []
    rejected_feedback: List[str] = []

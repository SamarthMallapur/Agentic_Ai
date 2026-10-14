from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class ApplicationStatus(str, Enum):
    SAVED = "SAVED"
    APPLIED = "APPLIED"
    OA = "OA"
    INTERVIEW = "INTERVIEW"
    TECHNICAL_INTERVIEW = "TECHNICAL_INTERVIEW"
    HR_INTERVIEW = "HR_INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"

class Application(BaseModel):
    id: Optional[int] = None
    company: str
    role: str
    job_description: str = ""
    application_date: Optional[str] = None
    source: str = ""
    status: ApplicationStatus = ApplicationStatus.SAVED
    resume_version: str = ""
    resume_score: Optional[int] = None
    interview_date: Optional[str] = None
    interview_stage: str = ""
    result: str = ""
    notes: str = ""
    follow_up_date: Optional[str] = None

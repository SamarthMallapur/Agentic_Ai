from pydantic import BaseModel, Field
from typing import List, Dict

class KeywordGap(BaseModel):
    matched_keywords: List[str]
    missing_keywords: List[str]
    partially_matched_keywords: List[str]
    keyword_frequency: Dict[str, int]
    priority: List[str]

class ResumeScore(BaseModel):
    ats_keyword_match_score: int = Field(..., ge=0, le=30)
    skills_alignment_score: int = Field(..., ge=0, le=25)
    experience_relevance_score: int = Field(..., ge=0, le=20)
    resume_quality_score: int = Field(..., ge=0, le=15)
    red_flags_score: int = Field(..., ge=0, le=10)
    total_score: int = Field(..., ge=0, le=100)
    red_flags: List[str]
    recommendations: List[str]

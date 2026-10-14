from pydantic import BaseModel
from typing import List, Dict

class ReportClaim(BaseModel):
    claim: str
    evidence: str
    source: str
    sample_size: int
    confidence: str # HIGH, MEDIUM, LOW

class MarketTrend(BaseModel):
    top_skills: List[str]
    rising_skills: List[str]
    common_roles: List[str]
    relevant_technologies: List[str]

class RecommendedAction(BaseModel):
    action: str
    why: str
    evidence: str
    effort: str
    expected_benefit: str

class PlacementReport(BaseModel):
    total_applications: int
    interviews: int
    offers: int
    rejections: int
    average_resume_score: float
    highest_resume_score: int
    lowest_resume_score: int
    most_common_weaknesses: List[str]
    market_trends: MarketTrend
    market_demand_comparison: Dict[str, bool] # skill -> has_skill
    strong_areas: List[str]
    weak_areas: List[str]
    frequently_missed_questions: List[str]
    recommended_actions: List[RecommendedAction]
    evidence_table: List[ReportClaim]

from pydantic import BaseModel
from typing import List, Optional

class InterviewQuestion(BaseModel):
    category: str  # Technical, Project, Behavioral, Resume, Weakness
    difficulty: str  # Easy, Medium, Hard
    question: str
    expected_answer_points: List[str]

class InterviewFeedback(BaseModel):
    technical_correctness: int  # 1-10
    relevance: int
    clarity: int
    structure: int
    confidence: int
    depth: int
    conciseness: int
    feedback: str

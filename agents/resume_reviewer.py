import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from google.adk.agents import Agent
from tools.resume_score import resume_score
from tools.keyword_gap import keyword_gap

def review_resume_tool(resume_text: str, jd_text: str) -> dict:
    """Scores a resume and finds keyword gaps."""
    score = resume_score(resume_text, jd_text)
    gaps = keyword_gap(resume_text, jd_text)
    return {
        "score": score.dict(),
        "gaps": gaps.dict()
    }

resume_reviewer_agent = Agent(
    name="resume_reviewer",
    model="gemini-3.1-flash-lite",
    description="Reviews a resume against a job description, providing a score and keyword gaps.",
    instruction="""
    You are an expert Resume Reviewer.
    Use the 'review_resume_tool' to analyze the provided resume against the job description.
    Present the results clearly:
    1. Total Score (out of 100)
    2. Missing High-Priority Keywords
    3. Formatting / Red Flags
    4. Top 3 actionable recommendations
    
    Ensure you rely purely on the output of the 'review_resume_tool'. Do not invent missing keywords or scores.
    """,
    tools=[review_resume_tool],
    output_key="resume_review_output"
)

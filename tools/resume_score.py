import os
from google import genai
from pydantic import BaseModel
import sys

# Add parent dir to path to import schemas
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from schemas.resume import ResumeScore

def get_gemini_client():
    return genai.Client()

def resume_score(resume_text: str, jd_text: str) -> ResumeScore:
    """Scores a resume against a job description using Gemini structured output."""
    client = get_gemini_client()
    
    prompt = f"""
    You are an expert ATS (Applicant Tracking System) and technical recruiter.
    Evaluate the following Resume against the Job Description.
    
    Use this strict rubric (Total 100 points):
    1. ATS / Keyword Match (0-30): Required tech keywords, tools, domain keywords.
    2. Skills Alignment (0-25): Relevant skills present and depth.
    3. Experience / Project Relevance (0-20): Relevant projects and evidence of impact.
    4. Resume Quality (0-15): Formatting, readability, section organization.
    5. Red Flags (0-10): Subtract points for red flags (missing sections, generic objective, poor formatting). Start at 10, deduct for issues.
    
    Job Description:
    {jd_text}
    
    Resume:
    {resume_text}
    """
    
    response = client.models.generate_content(
        model='gemini-3.8-flash',
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': ResumeScore,
            'temperature': 0.1,
        },
    )
    
    return response.parsed

import os
from google import genai
import sys

from dotenv import load_dotenv
load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from schemas.resume import KeywordGap

def get_gemini_client():
    return genai.Client()

def keyword_gap(resume_text: str, jd_text: str) -> KeywordGap:
    """Identifies missing keywords and classifies them by priority."""
    client = get_gemini_client()
    
    prompt = f"""
    You are an expert career coach. Analyze the given Resume and Job Description.
    Extract technical skills, tools, and domain keywords.
    Identify matched, missing, and partially matched keywords.
    Provide the frequency of required keywords in the JD.
    Categorize the missing keywords into priority: HIGH, MEDIUM, LOW.
    
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
            'response_schema': KeywordGap,
            'temperature': 0.1,
        },
    )
    
    return response.parsed

import os
from google import genai
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from schemas.interview import InterviewFeedback

def get_gemini_client():
    return genai.Client()

def generate_interview_questions(profile: dict, jd: str, skill_gaps: dict):
    client = get_gemini_client()
    
    prompt = f"""
    You are an expert technical interviewer. Generate 5 mock interview questions based on the student's profile, the job description, and identified skill gaps.
    Include 1 Technical, 1 Project-based, 1 Behavioral, 1 Resume-based, and 1 Weakness-based question.
    Format as JSON array of objects with keys: category, difficulty, question, expected_answer_points.
    
    Profile: {profile}
    JD: {jd}
    Skill Gaps: {skill_gaps}
    """
    
    response = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'temperature': 0.7,
        },
    )
    
    return response.text

def evaluate_interview_answer(question: str, answer: str) -> InterviewFeedback:
    client = get_gemini_client()
    
    prompt = f"""
    Evaluate the student's answer to the interview question.
    Question: {question}
    Student Answer: {answer}
    
    Score out of 10 for: technical_correctness, relevance, clarity, structure, confidence, depth, conciseness.
    Provide constructive feedback using the STAR method if behavioral.
    """
    
    response = client.models.generate_content(
        model='gemini-3.1-flash-lite',
        contents=prompt,
        config={
            'response_mime_type': 'application/json',
            'response_schema': InterviewFeedback,
            'temperature': 0.2,
        },
    )
    
    return response.parsed

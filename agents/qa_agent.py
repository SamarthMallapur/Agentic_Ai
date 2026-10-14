import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from google.adk.agents import Agent

qa_agent = Agent(
    name="qa_agent",
    model="gemini-3.1-flash-lite",
    description="QA & Governance Agent that ensures claims have evidence and confidence labels.",
    instruction="""
    You are the final QA/Governance Agent.
    Review the proposed output for the student.
    
    Rules:
    1. NEVER fabricate company information, job stats, or market trends.
    2. If a claim lacks evidence in the context, remove or caveat it heavily.
    3. Ensure low confidence claims are explicitly labeled: "LOW CONFIDENCE".
    4. Ensure no new skills are being added to the student's resume without the caveat: "Consider learning this skill."
    5. Output the final safe and governed response.
    """,
    output_key="qa_output"
)

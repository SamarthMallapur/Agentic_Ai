import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from google.adk.agents import Agent

report_generator = Agent(
    name="report_generator",
    model="gemini-3.1-flash-lite",
    description="Generates the weekly placement readiness report.",
    instruction="""
    You are the Report Generator.
    Take the inputs from the Market Analyst, Application Tracker, and Resume Reviewer.
    Compile a structured Weekly Placement Readiness Report.
    The report MUST contain:
    1. Application Summary
    2. Resume Performance
    3. Market Trends
    4. Personal Skill Gaps
    5. Interview Readiness
    6. Recommended Actions
    7. Evidence Table
    """,
    output_key="weekly_report"
)

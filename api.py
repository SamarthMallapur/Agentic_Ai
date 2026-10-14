import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import json

from memory.profile_memory import ProfileMemory
from tools.application_tracker import ApplicationTracker
from tools.market_analysis import MarketAnalysis
from reports.weekly_report import generate_weekly_report
from agents.resume_reviewer import review_resume_tool
from agents.interview_coach import generate_interview_questions
from tools.resume_parser import parse_resume

app = FastAPI(title="Placement Readiness API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow local React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

profile_db = ProfileMemory()
app_tracker = ApplicationTracker()
market_db = MarketAnalysis()

class ProfileUpdate(BaseModel):
    profile_data: Dict

class ApplicationCreate(BaseModel):
    company: str
    role: str
    job_description: Optional[str] = ""
    status: Optional[str] = "SAVED"

class InterviewGenerateReq(BaseModel):
    job_description: str
    missing_skills: List[str]

@app.get("/api/dashboard")
def get_dashboard():
    apps = app_tracker.get_applications()
    interviews = [a for a in apps if a.get('status') in ['INTERVIEW', 'TECHNICAL_INTERVIEW', 'HR_INTERVIEW']]
    offers = [a for a in apps if a.get('status') == 'OFFER']
    return {
        "readiness_score": "82 / 100",
        "total_applications": len(apps),
        "interviews": len(interviews),
        "offers": len(offers)
    }

@app.get("/api/profile")
def get_profile():
    return profile_db.get_profile()

@app.post("/api/profile")
def update_profile(req: ProfileUpdate):
    profile_db.update_profile(req.profile_data)
    return {"status": "success"}

@app.get("/api/applications")
def get_applications():
    return app_tracker.get_applications()

@app.post("/api/applications")
def add_application(req: ApplicationCreate):
    app_id = app_tracker.add_application(req.model_dump())
    return {"status": "success", "id": app_id}

@app.get("/api/market")
def get_market_trends():
    return market_db.get_market_statistics()

@app.get("/api/report")
def get_report():
    return generate_weekly_report().model_dump()

@app.post("/api/resume/analyze")
async def analyze_resume(
    jd: str = Form(...),
    resume_text: str = Form(None),
    file: UploadFile = File(None)
):
    text_to_analyze = ""
    if file:
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(await file.read())
            temp_pdf_path = temp_pdf.name
        try:
            text_to_analyze = parse_resume(temp_pdf_path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error parsing PDF: {str(e)}")
        finally:
            os.remove(temp_pdf_path)
    elif resume_text:
        text_to_analyze = resume_text
    else:
        raise HTTPException(status_code=400, detail="Must provide either resume_text or file.")

    try:
        result = review_resume_tool(text_to_analyze, jd)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interview/generate")
def generate_interview(req: InterviewGenerateReq):
    profile = profile_db.get_profile()
    try:
        questions = generate_interview_questions(
            profile, 
            req.job_description, 
            {"missing": req.missing_skills}
        )
        # Gemini can return markdown code blocks, try to parse JSON
        try:
            clean_questions = json.loads(questions.strip("```json\n").strip("\n```"))
            return clean_questions
        except json.JSONDecodeError:
            return {"raw": questions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)

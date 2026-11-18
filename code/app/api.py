"""FastAPI backend. It also serves the built web app from one address."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel

from . import agents, config, datasets, db, governance, llm, memory, orchestrator, research
from .tools import STATUSES, application_tracker, read_resume_file


@asynccontextmanager
async def lifespan(_app):
    datasets.setup()
    yield


app = FastAPI(title="Placement Readiness Companion", lifespan=lifespan)


def guarded(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


class ReviewRequest(BaseModel):
    resume_text: str = ""
    jd: str = ""
    company: str = ""
    role: str = ""
    application_id: int | None = None
    continue_anyway: bool = False


class FeedbackRequest(BaseModel):
    suggestion: str
    decision: str
    skill: str = ""
    reason: str = ""
    context: str = ""


class ApplicationRequest(BaseModel):
    company: str | None = None
    role: str | None = None
    job_description: str | None = None
    status: str | None = None
    applied_on: str | None = None
    follow_up_on: str | None = None
    notes: str | None = None


class QuestionsRequest(BaseModel):
    jd: str
    role: str = ""
    application_id: int | None = None


class AnswerRequest(BaseModel):
    question: dict
    answer: str
    application_id: int | None = None


@app.get("/api/status")
def status():
    return {"ai_enabled": llm.available(), "model": config.PRIMARY_MODEL if llm.available() else None,
            "dataset": governance.dataset_info(), "statuses": STATUSES}


@app.get("/api/dashboard")
def dashboard():
    return orchestrator.dashboard()


@app.get("/api/profile")
def get_profile():
    return memory.get_profile()


@app.put("/api/profile")
def put_profile(data: dict):
    return memory.save_profile(data)


@app.post("/api/resume/upload")
async def upload_resume(file: UploadFile = File(...)):
    try:
        text = read_resume_file(file.filename or "", await file.read())
    except ValueError as exc:
        raise HTTPException(400, str(exc))
    except Exception:
        raise HTTPException(400, "That file could not be read. Try a text-based PDF, or paste the resume.")
    if len(text.split()) < 20:
        raise HTTPException(400, "No readable text was found. A scanned PDF will not work, so please paste the text.")
    return {"text": text}


@app.post("/api/review")
def review(req: ReviewRequest):
    return agents.review_resume(req.resume_text, req.jd, req.company, req.role, req.application_id, req.continue_anyway)


@app.get("/api/review/latest")
def review_latest():
    return agents.latest_review()


@app.get("/api/feedback")
def feedback():
    return memory.all_feedback()


@app.post("/api/feedback")
def add_feedback(req: FeedbackRequest):
    return guarded(memory.add_feedback, req.suggestion, req.decision, req.skill, req.reason, req.context)


@app.get("/api/applications")
def applications():
    return application_tracker("list")["applications"]


@app.post("/api/applications")
def add_application(req: ApplicationRequest):
    return guarded(application_tracker, "add", **req.model_dump(exclude_none=True))


@app.patch("/api/applications/{application_id}")
def update_application(application_id: int, req: ApplicationRequest):
    return guarded(application_tracker, "update", application_id, **req.model_dump(exclude_unset=True))


@app.delete("/api/applications/{application_id}")
def delete_application(application_id: int):
    return guarded(application_tracker, "delete", application_id)


@app.post("/api/interview/questions")
def interview_questions(req: QuestionsRequest):
    if len(req.jd.split()) < 5:
        raise HTTPException(400, "Choose an application that has a job description, or paste one.")
    return agents.interview_questions(req.jd, req.role, req.application_id)


@app.post("/api/interview/answer")
def interview_answer(req: AnswerRequest):
    return guarded(agents.evaluate_answer, req.question, req.answer, req.application_id)


@app.get("/api/market")
def market():
    profile = memory.get_profile()
    return research.run(profile["target_roles"], profile["skills"])


@app.get("/api/postings/{posting_id}")
def posting(posting_id: int):
    rows = db.query("SELECT * FROM postings WHERE id = ?", (posting_id,))
    if not rows:
        raise HTTPException(404, "Posting not found.")
    return rows[0]


@app.post("/api/report")
def create_report():
    return orchestrator.weekly_report()


@app.get("/api/report/latest")
def report_latest():
    return orchestrator.latest_report()


@app.get("/api/report/latest.md", response_class=PlainTextResponse)
def report_markdown():
    rows = db.query("SELECT markdown FROM reports ORDER BY id DESC LIMIT 1")
    if not rows:
        raise HTTPException(404, "Generate a report first.")
    return PlainTextResponse(rows[0]["markdown"], headers={"Content-Disposition": "attachment; filename=weekly_report.md"})


@app.get("/{path:path}", include_in_schema=False)
def web_app(path: str):
    if path.startswith("api/"):
        raise HTTPException(404, "Not found.")
    root = config.WEB_DIR.resolve()
    target = (root / path).resolve()
    if path and target.is_file() and target.is_relative_to(root):
        return FileResponse(target)
    return FileResponse(root / "index.html")

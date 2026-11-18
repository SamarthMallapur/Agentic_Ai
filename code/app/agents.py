"""The specialist agents: Intake, Resume-Reviewer and Interview-Coach.

Rules and scoring are deterministic. Gemini only adds wording, and its output is
checked before use. If Gemini is unavailable, each agent still returns a result.
"""
import hashlib
import json
import re

from pydantic import BaseModel, Field

from . import config, db, governance, llm, memory, prompts
from .insights import delivery
from .tools import application_tracker, bullets, keyword_gap, resume_score
from .vocab import extract_skills


# ---------------------------------------------------------------- Intake
def intake(resume: str, jd: str, company: str = "", role: str = "") -> dict:
    """Clarify missing context before any drafting happens."""
    blocking, questions = [], []
    if len(resume.split()) < 80:
        blocking.append({"field": "resume", "question": "Please paste or upload your full resume (at least 80 words)."})
    if len(jd.split()) < 15:
        blocking.append({"field": "jd", "question": "Please paste the job description you are applying to."})
    if not blocking and (len(jd.split()) < 40 or len(extract_skills(jd)) < 3):
        questions.append({"field": "jd", "question": "This job description is short or names few skills. Can you paste the full version?"})
    if not role.strip():
        questions.append({"field": "role", "question": "Which role is this application for?"})
    if not company.strip():
        questions.append({"field": "company", "question": "Which company is this for?"})
    return {"ready": not blocking and not questions, "can_continue": not blocking, "questions": blocking + questions}


# ---------------------------------------------------------------- Resume-Reviewer
class Rewrite(BaseModel):
    original: str
    rewrite: str


class RewriteList(BaseModel):
    rewrites: list[Rewrite] = Field(default_factory=list)


def _rec(kind: str, text: str, skill: str = "", confidence: str = "Medium", basis: str = "") -> dict:
    rec_id = hashlib.sha1(text.encode()).hexdigest()[:10]
    return {"id": rec_id, "type": kind, "text": text, "skill": skill, "confidence": confidence, "basis": basis}


def _recommendations(score: dict) -> list[dict]:
    gap, recs = score["gap"], []
    for item in gap["missing"][:5]:
        confidence = "Medium" if item["priority"] == "HIGH" else "Low"
        recs.append(_rec("add_skill", f"The JD asks for {item['skill']} ({item['priority']} priority) and your resume does not show it.",
                         item["skill"], confidence, f"JD: \"{item['jd_evidence']}\""))
    for item in gap["partial"][:3]:
        near = ", ".join(item["related_resume_skills"])
        recs.append(_rec("add_skill", f"You show {near}, which is related to {item['skill']}. Mention {item['skill']} directly if you have used it.",
                         item["skill"], "Medium", f"JD: \"{item['jd_evidence']}\""))
    for flag in score["red_flags"]:
        recs.append(_rec("fix", f"{flag['flag']}: {flag['fix']}", confidence="High", basis="Red-flag list"))
    for check in score["checklist"]:
        if not check["passed"]:
            recs.append(_rec("fix", f"Formatting: {check['item']} is not met.", confidence="High", basis="Formatting checklist"))
    return recs


def _apply_memory(recs: list[dict]) -> tuple[list[dict], list[dict]]:
    shown, hidden = [], []
    for rec in recs:
        match = memory.retrieve_feedback(rec["text"], rec["skill"])
        if match and match["decision"] == "rejected":
            hidden.append({**rec, "memory_reason": match["reason"] or "You rejected similar advice earlier."})
            continue
        if match:
            rec = {**rec, "memory_note": "You accepted similar advice before."}
        shown.append(rec)
    return shown, hidden


def _rewrites(resume: str, role: str, missing: list[str]) -> tuple[list[dict], list[dict]]:
    candidates = [b for b in bullets(resume) if len(b.split()) >= 4][:4]
    if not candidates:
        return [], []
    prompt = prompts.REWRITE_BULLETS.format(
        skill=config.SKILL_FILE.read_text(encoding="utf-8"), missing_skills=", ".join(missing) or "none",
        role=role or "not given", bullets="\n".join(f"- {b}" for b in candidates),
    )
    result = llm.generate("rewrite_bullets", prompt, RewriteList, temperature=0.2)
    accepted, rejected = [], []
    for item in result.rewrites if result else []:
        if item.original not in candidates:
            rejected.append({"rewrite": item.rewrite, "problems": ["Original bullet not found in the resume"]})
            continue
        problems = governance.check_rewrite(item.original, item.rewrite)
        (rejected.append({"rewrite": item.rewrite, "problems": problems}) if problems
         else accepted.append({"original": item.original, "rewrite": item.rewrite}))
    return accepted, rejected


def review_resume(resume: str, jd: str, company: str = "", role: str = "", application_id: int | None = None,
                  continue_anyway: bool = False, use_llm: bool = True) -> dict:
    """Full guided flow: intake -> rubric -> memory -> rewrite -> QA -> save."""
    check = intake(resume, jd, company, role)
    if not check["can_continue"] or (not check["ready"] and not continue_anyway):
        return {"status": "needs_input", **check}

    db.set_state("todays_application", {"application_id": application_id, "company": company, "role": role})
    score = resume_score(resume, jd, role)
    assumptions = [q["question"] for q in check["questions"]]
    if assumptions:
        score["confidence"], score["confidence_reason"] = "Low", "You continued without all the requested details."

    shown, hidden = _apply_memory(_recommendations(score))
    if score["confidence"] == "Low":
        shown = [{**r, "confidence": "Low"} if r["type"] == "add_skill" else r for r in shown]
    missing = [i["skill"] for i in score["gap"]["missing"]]
    rewrites, rejected = _rewrites(resume, role, missing) if use_llm else ([], [])
    result = {
        "status": "done", **score, "company": company, "role": role, "application_id": application_id,
        "inputs": {"resume_text": resume, "jd": jd},
        "assumptions": assumptions, "recommendations": governance.qa_recommendations(shown), "hidden_by_memory": hidden,
        "rewrites": rewrites,
        "qa": {
            "skill_claims_with_honesty_note": sum(1 for r in shown if r["type"] == "add_skill"),
            "rewrites_rejected": rejected,
            "rewrite_source": "Gemini, checked by QA" if llm.available() and use_llm else "Not generated (no Gemini key)",
        },
    }
    result["review_id"] = db.execute(
        "INSERT INTO reviews (application_id, company, role, score, confidence, result, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (application_id, company, role, score["total"], score["confidence"], json.dumps(result), db.now()),
    )
    db.set_state("last_review_id", result["review_id"])
    if application_id:
        application_tracker("update", application_id, resume_score=score["total"])
    return result


def latest_review() -> dict | None:
    rows = db.query("SELECT id, result FROM reviews ORDER BY id DESC LIMIT 1")
    return {**json.loads(rows[0]["result"]), "review_id": rows[0]["id"]} if rows else None


def reviewer_worker() -> dict:
    """Weekly-report worker: re-score the current resume against tracked JDs."""
    resume = memory.get_profile()["resume_text"]
    apps = [a for a in application_tracker("list")["applications"]
            if a["job_description"] and a["status"] not in ("REJECTED", "WITHDRAWN")]
    if not resume or not apps:
        return {"reviewed": [], "note": "Add a resume and at least one application with a JD."}
    reviewed, missing, weakest = [], {}, {}
    for app in apps:
        score = resume_score(resume, app["job_description"], app["role"])
        reviewed.append({"application_id": app["id"], "company": app["company"], "role": app["role"],
                         "score": score["total"], "confidence": score["confidence"]})
        for item in score["gap"]["missing"]:
            missing.setdefault(item["skill"], []).append(app["id"])
        for part in score["breakdown"]:
            weakest[part["criterion"]] = weakest.get(part["criterion"], 0) + part["score"] / part["max"]
    scores = [r["score"] for r in reviewed]
    return {
        "reviewed": reviewed, "average": round(sum(scores) / len(scores)), "highest": max(scores), "lowest": min(scores),
        "common_missing": [{"skill": s, "application_ids": ids} for s, ids in sorted(missing.items(), key=lambda kv: -len(kv[1]))[:5]],
        "weakest_criterion": min(weakest, key=weakest.get),
    }


# ---------------------------------------------------------------- Interview-Coach
class Question(BaseModel):
    category: str
    question: str
    answer_points: list[str]


class QuestionList(BaseModel):
    questions: list[Question]


class AnswerScore(BaseModel):
    relevance: int = Field(ge=0, le=10)
    structure: int = Field(ge=0, le=10)
    specificity: int = Field(ge=0, le=10)
    clarity: int = Field(ge=0, le=10)
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)


TECH_BANK = {
    "SQL": ("What is the difference between INNER JOIN and LEFT JOIN, and when would you add an index?", ["Join behaviour", "Example query", "Index read and write trade-off"]),
    "Python": ("How do lists, tuples and dictionaries differ, and when would you pick each?", ["Mutability", "Lookup cost", "A practical example"]),
    "Docker": ("What problem does a Docker image solve, and how is it different from a container?", ["Image versus container", "Reproducible environments", "A Dockerfile example"]),
    "REST APIs": ("How would you design a REST endpoint for creating an order?", ["Method and path", "Status codes and validation", "Idempotency"]),
    "System Design": ("How would you design a URL shortener for high read traffic?", ["Requirements and data model", "Caching", "Scaling and failure handling"]),
    "Data Structures & Algorithms": ("How would you detect a cycle in a linked list? State the complexity.", ["Two-pointer idea", "Time and space complexity", "Edge cases"]),
    "React": ("When does a React component re-render, and how can you avoid needless renders?", ["State and props", "Memoisation", "Measuring first"]),
    "Machine Learning": ("How do you detect and reduce overfitting?", ["Train versus validation gap", "Regularisation", "More data or simpler models"]),
}


def _question_bank(role: str, gaps: list[str], skills: list[str]) -> list[dict]:
    focus = next((s for s in gaps + skills if s in TECH_BANK), None)
    skill = focus or (gaps[0] if gaps else skills[0] if skills else "your main technical skill")
    question, points = TECH_BANK.get(skill, (f"Explain {skill} to a junior teammate and describe where you would use it.",
                                             ["Core concept", "Concrete use case", "Trade-offs"]))
    weak = gaps[0] if gaps else "an area you are still improving"
    known = skills[0] if skills else "a skill on your resume"
    return [
        {"category": "Technical", "skill": skill, "question": question, "answer_points": points},
        {"category": "Project", "skill": known, "question": f"Walk me through a project where you used {known}. What was hardest?", "answer_points": ["Problem and your role", "Key decision", "Measured result"]},
        {"category": "Behavioral", "skill": "", "question": "Tell me about a time you disagreed with a teammate. What happened?", "answer_points": ["Situation and task", "Action you took", "Result and learning"]},
        {"category": "Resume", "skill": known, "question": f"Your resume lists {known}. What is the most difficult thing you have built with it?", "answer_points": ["Specific work", "Your contribution", "What you would change"]},
        {"category": "Weakness", "skill": weak, "question": f"This {role or 'role'} may need {weak}. How would you close that gap in your first month?", "answer_points": ["Honest current level", "Concrete learning plan", "How you would show progress"]},
    ]


def interview_questions(jd: str, role: str = "", application_id: int | None = None) -> dict:
    profile = memory.get_profile()
    gap = keyword_gap(profile["resume_text"], jd)
    gaps = [i["skill"] for i in gap["missing"] + gap["partial"]]
    skills = [i["skill"] for i in gap["matched"]] or profile["skills"]
    bank = _question_bank(role, gaps, skills)
    prompt = prompts.INTERVIEW_QUESTIONS.format(role=role or "not given", skills=", ".join(skills[:12]) or "not given",
                                                gaps=", ".join(gaps[:6]) or "none", resume=profile["resume_text"][:2000], jd=jd[:2000])
    generated = llm.generate("interview_questions", prompt, QuestionList, temperature=0.5)
    source, questions = "Question bank (no AI used)", bank
    if generated and len(generated.questions) >= 5:
        evidence = f"{profile['resume_text']} {jd}"
        safe = [q for q in generated.questions[:5] if not governance.check_narrative(q.question, evidence)]
        if len(safe) == 5:
            source = "Gemini, checked by QA"
            questions = [{**q.model_dump(), "skill": next(iter(extract_skills(q.question)), "")} for q in safe]
    return {"questions": questions, "gaps": gaps[:6], "source": source, "application_id": application_id}


def _heuristic_score(question: dict, answer: str) -> dict:
    lowered, words = answer.lower(), answer.split()
    terms = {w for p in question.get("answer_points", []) for w in re.findall(r"[a-z]{5,}", p.lower())}
    relevance = min(10, 2 + round(8 * sum(1 for t in terms if t in lowered) / max(len(terms), 1) * 1.5))
    markers = ["situation", "task", "action", "result", "first", "then", "because", "finally", "so that"]
    structure = min(10, 2 + 2 * sum(1 for m in markers if m in lowered))
    specificity = min(10, 2 + 3 * len(re.findall(r"\d+", answer)) + 2 * len(extract_skills(answer)))
    clarity = 8 if 50 <= len(words) <= 220 else 5 if 20 <= len(words) < 50 or 220 < len(words) <= 350 else 2
    improvements = []
    if relevance < 6:
        improvements.append("Cover these points directly: " + "; ".join(question.get("answer_points", [])))
    if structure < 6:
        improvements.append("Use a clear order, such as Situation, Task, Action, Result.")
    if specificity < 6:
        improvements.append("Add a concrete tool, example or measured result from your own work.")
    if clarity < 6:
        improvements.append("Aim for roughly 50 to 220 words.")
    return {"relevance": relevance, "structure": structure, "specificity": specificity, "clarity": clarity,
            "strengths": ["Answer has a usable length."] if clarity >= 8 else [], "improvements": improvements}


def evaluate_answer(question: dict, answer: str, application_id: int | None = None, use_llm: bool = True,
                    spoken_seconds: float | None = None) -> dict:
    if len(answer.split()) < 5:
        raise ValueError("Please write a fuller answer before asking for feedback.")
    prompt = prompts.EVALUATE_ANSWER.format(category=question.get("category", ""), question=question.get("question", ""),
                                            points="; ".join(question.get("answer_points", [])), answer=answer[:3000])
    scored = llm.generate("evaluate_answer", prompt, AnswerScore, temperature=0.1) if use_llm else None
    if scored:
        feedback, method, confidence = scored.model_dump(), "Gemini", "Medium"
    else:
        feedback, method, confidence = _heuristic_score(question, answer), "Rule-based estimate", "Low"
    feedback["delivery"] = delivery(answer, spoken_seconds)
    parts = [feedback[k] for k in ("relevance", "structure", "specificity", "clarity")]
    score = round(sum(parts) / len(parts), 1)
    db.execute(
        "INSERT INTO interview_attempts (application_id, category, skill, question, answer, score, method, confidence, feedback, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (application_id, question.get("category", "General"), question.get("skill", ""), question.get("question", ""), answer,
         score, method, confidence, json.dumps(feedback), db.now()),
    )
    note = f"{governance.LOW_LABEL}: rule-based estimate, not a judgment of correctness." if confidence == "Low" else "AI feedback. Check it against your own judgment."
    return {"score": score, "method": method, "confidence": confidence, "note": note, **feedback}


def coach_worker() -> dict:
    """Weekly-report worker: summarise practice and find weak categories."""
    attempts = db.query("SELECT * FROM interview_attempts ORDER BY id DESC")
    if not attempts:
        return {"attempts": 0, "average": None, "weak_categories": [], "note": "No mock answers yet."}
    by_category = {}
    for attempt in attempts:
        by_category.setdefault(attempt["category"], []).append(attempt["score"])
    averages = {c: round(sum(v) / len(v), 1) for c, v in by_category.items()}
    return {
        "attempts": len(attempts), "average": round(sum(a["score"] for a in attempts) / len(attempts), 1),
        "by_category": averages, "weak_categories": [c for c, v in sorted(averages.items(), key=lambda kv: kv[1]) if v < 6][:3],
        "attempt_ids": [a["id"] for a in attempts[:5]],
        "confidence": "Low" if any(a["confidence"] == "Low" for a in attempts) or len(attempts) < 5 else "Medium",
    }

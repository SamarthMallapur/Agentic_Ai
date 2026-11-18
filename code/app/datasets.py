"""Load job postings and create the demo student."""
import csv
from datetime import timedelta

from . import agents, config, db, memory
from .tools import application_tracker
from .vocab import extract_skills

csv.field_size_limit(2**24)
MAX_ROWS_PER_FILE = 5000
TITLE = ("job title", "jobtitle", "title", "position")
DESCRIPTION = ("job description", "jobdescription", "description", "job_description")
COMPANY = ("company", "company name", "company_name")
LOCATION = ("location", "joblocation_address", "job location")
SKILLS = ("skills", "key skills", "skill")
DATE = ("postdate", "posted_on", "date posted", "posted date", "date")


def _pick(row: dict, names) -> str:
    lowered = {(k or "").strip().lower(): v for k, v in row.items()}
    return next(((lowered[n] or "").strip() for n in names if lowered.get(n)), "")


def _read_postings(path, is_demo=False) -> list[tuple]:
    rows = []
    with open(path, encoding="utf-8", errors="replace", newline="") as handle:
        for number, row in enumerate(csv.DictReader(handle), start=2):
            title, description = _pick(row, TITLE), _pick(row, DESCRIPTION)
            if not title or len(description) < 30:
                continue
            posted = _pick(row, DATE)[:10]
            rows.append((title[:200], _pick(row, COMPANY)[:200], _pick(row, LOCATION)[:200], description[:6000],
                         _pick(row, SKILLS)[:1000], posted if posted[:2] in ("19", "20") else None, path.name, number, int(is_demo)))
            if len(rows) >= MAX_ROWS_PER_FILE:
                break
    return rows


def load_postings() -> dict:
    """Use recognised CSV files in data/raw. Otherwise use the labelled demo data."""
    rows, used = [], []
    for path in sorted(config.RAW_DIR.glob("*.csv")):
        found = _read_postings(path)
        if found:
            rows += found
            used.append(path.name)
    if not rows:
        rows, used = _read_postings(config.DEMO_POSTINGS, True), [config.DEMO_POSTINGS.name]
    with db.connect() as conn:
        conn.execute("DELETE FROM postings")
        conn.executemany(
            "INSERT INTO postings (title, company, location, description, skills, posted_on, source, source_row, is_demo) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", rows)
    return {"rows": len(rows), "files": used}


def seed_demo_student() -> None:
    resume = (config.DEMO_RESUMES / "backend_student.txt").read_text(encoding="utf-8")
    memory.save_profile({
        "name": "Demo Student", "education": "B.E. Computer Science", "graduation_year": "2027",
        "target_roles": ["Backend Developer", "Software Engineer"], "skills": list(extract_skills(resume)),
        "weak_areas": ["System Design"], "resume_text": resume,
    })
    memory.add_feedback("Add Kubernetes to your skills section.", "rejected", "Kubernetes",
                        "I have never used Kubernetes.", "Demo seed")
    memory.add_feedback("Show API response-time results in your project bullets.", "accepted", "", "Good, I measured this.", "Demo seed")

    today = db.today()
    demo_apps = [
        ("Demo Company 03", "Backend Developer", "backend_developer.txt", "INTERVIEW", -12, 1),
        ("Demo Company 11", "Software Engineer", "software_engineer.txt", "APPLIED", -5, 5),
        ("Demo Company 18", "Data Analyst", "data_analyst.txt", "SAVED", None, None),
    ]
    first_id = None
    for company, role, jd_file, status, applied, follow_up in demo_apps:
        jd = (config.DEMO_JDS / jd_file).read_text(encoding="utf-8")
        app = application_tracker(
            "add", company=company, role=role, job_description=jd, status=status,
            applied_on=(today + timedelta(days=applied)).isoformat() if applied is not None else None,
            follow_up_on=(today + timedelta(days=-follow_up)).isoformat() if follow_up else None,
        )
        first_id = first_id or app["id"]
        agents.review_resume(resume, jd, company, role, app["id"], use_llm=False)

    agents.evaluate_answer(
        {"category": "Behavioral", "question": "Tell me about a time you disagreed with a teammate.",
         "answer_points": ["Situation and task", "Action you took", "Result and learning"]},
        "We disagreed about the database design and I explained my view, then we picked one.", first_id, use_llm=False)
    agents.evaluate_answer(
        {"category": "Technical", "skill": "SQL", "question": "What is the difference between INNER JOIN and LEFT JOIN?",
         "answer_points": ["Join behaviour", "Example query", "Index read and write trade-off"]},
        "An INNER JOIN returns only matching rows, because both tables must have the key. A LEFT JOIN keeps every row from the "
        "left table. For example, in my FastAPI project I joined 2 tables, users and orders, then added an index on user_id, so "
        "reads became faster, although writes do a little more work.", first_id, use_llm=False)


def setup(reset: bool = False) -> None:
    if reset:
        config.db_path().unlink(missing_ok=True)
    db.init_db()
    if not db.query("SELECT 1 FROM postings LIMIT 1"):
        load_postings()
    if not db.query("SELECT 1 FROM profile LIMIT 1"):
        seed_demo_student()

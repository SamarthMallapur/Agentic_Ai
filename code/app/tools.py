"""The three tools named in the brief: resume_score, keyword_gap, application_tracker."""
import io
import re
from collections import Counter

from . import db
from .vocab import extract_skills, has_skill, related_to

RUBRIC = {
    "ATS keyword match": 30,
    "Skills alignment": 25,
    "Experience relevance": 20,
    "Resume quality": 15,
    "Red flags": 10,
}
PRIORITY_WEIGHT = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
STATUSES = ["SAVED", "APPLIED", "OA", "INTERVIEW", "OFFER", "REJECTED", "WITHDRAWN"]
ACTIVE_STATUSES = {"SAVED", "APPLIED", "OA", "INTERVIEW"}

HEADINGS = {
    "summary": ["summary", "objective", "career objective", "profile", "about me"],
    "education": ["education", "academics", "academic background"],
    "skills": ["skills", "technical skills", "core skills", "key skills"],
    "experience": ["experience", "work experience", "professional experience", "employment", "internship", "internships"],
    "projects": ["projects", "academic projects", "personal projects", "key projects"],
    "certifications": ["certifications", "certificates", "courses"],
    "achievements": ["achievements", "awards", "extracurricular", "positions of responsibility"],
}
_HEADING_LOOKUP = {name: section for section, names in HEADINGS.items() for name in names}
ACTION_VERBS = (
    "built developed designed implemented created led optimized optimised reduced improved automated deployed "
    "analyzed analysed delivered launched migrated integrated engineered increased managed tested refactored"
).split()
STOPWORDS = set(
    "the a an and or to of in on for with from by at as is are be will you your we our this that it their they "
    "who have has can must should able using use work working team role job candidate experience skills required "
    "requirements responsibilities strong good knowledge understanding looking join years year plus nice preferred".split()
)


def parse_sections(resume: str) -> dict[str, str]:
    sections, current = {}, "header"
    for line in (resume or "").splitlines():
        key = re.sub(r"[^a-z ]", "", line.lower()).strip()
        if len(line.strip()) < 40 and key in _HEADING_LOOKUP:
            current = _HEADING_LOOKUP[key]
            sections.setdefault(current, "")
            continue
        sections[current] = sections.get(current, "") + line + "\n"
    return sections


def bullets(resume: str) -> list[str]:
    return [
        re.sub(r"^\s*[-*•●▪]\s*", "", line).strip()
        for line in (resume or "").splitlines()
        if re.match(r"^\s*[-*•●▪]\s+\S", line)
    ]


def _classify_jd_skills(jd: str) -> dict[str, dict]:
    """Decide how important each JD skill is from the sentence that mentions it."""
    found = {}
    for sentence in re.split(r"(?<=[.;!?])\s+|\n+", jd or ""):
        for skill in extract_skills(sentence):
            lowered = sentence.lower()
            if re.search(r"nice to have|good to have|preferred|bonus|a plus|is a plus|desirable", lowered):
                priority = "LOW"
            elif re.search(r"familiar|exposure|basic|awareness", lowered):
                priority = "MEDIUM"
            else:
                priority = "HIGH"
            entry = found.setdefault(skill, {"priority": priority, "evidence": sentence.strip()[:180]})
            if PRIORITY_WEIGHT[priority] > PRIORITY_WEIGHT[entry["priority"]]:
                entry.update(priority=priority, evidence=sentence.strip()[:180])
    counts = extract_skills(jd)
    for skill, entry in found.items():
        entry["mentions"] = counts.get(skill, 1)
    return found


def keyword_gap(resume: str, jd: str) -> dict:
    """Tool: compare JD skills with the resume as matched, partial or missing."""
    jd_skills = _classify_jd_skills(jd)
    resume_skills = extract_skills(resume)
    matched, partial, missing = [], [], []
    for skill, info in sorted(jd_skills.items(), key=lambda kv: (-PRIORITY_WEIGHT[kv[1]["priority"]], kv[0])):
        item = {"skill": skill, "priority": info["priority"], "jd_mentions": info["mentions"], "jd_evidence": info["evidence"]}
        if skill in resume_skills:
            matched.append(item)
            continue
        near = sorted(related_to(skill) & set(resume_skills))
        if near:
            partial.append({**item, "related_resume_skills": near})
        else:
            missing.append(item)
    total = sum(PRIORITY_WEIGHT[i["priority"]] for i in jd_skills.values())
    earned = sum(PRIORITY_WEIGHT[i["priority"]] for i in matched) + 0.5 * sum(PRIORITY_WEIGHT[i["priority"]] for i in partial)
    return {
        "matched": matched,
        "partial": partial,
        "missing": missing,
        "jd_skill_count": len(jd_skills),
        "coverage_pct": round(100 * earned / total) if total else 0,
    }


def formatting_checklist(resume: str) -> list[dict]:
    sections = parse_sections(resume)
    items = bullets(resume)
    words = len(resume.split())
    numeric = [b for b in items if re.search(r"\d", b)]
    verbs = [b for b in items if b.split() and b.split()[0].lower().strip(",.") in ACTION_VERBS]
    checks = [
        ("Email address present", bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", resume))),
        ("Phone number present", bool(re.search(r"(?:\+?\d[\s-]?){10,13}", resume))),
        ("Education section", "education" in sections),
        ("Skills section", "skills" in sections),
        ("Experience or projects section", "experience" in sections or "projects" in sections),
        ("At least 4 bullet points", len(items) >= 4),
        ("Length between 200 and 1000 words", 200 <= words <= 1000),
        ("At least 2 bullets with numbers", len(numeric) >= 2),
        ("At least 3 bullets start with an action verb", len(verbs) >= 3),
    ]
    return [{"item": item, "passed": passed} for item, passed in checks]


def red_flags(resume: str, gap: dict | None = None) -> list[dict]:
    lowered = resume.lower()
    sections = parse_sections(resume)
    evidence = sections.get("experience", "") + sections.get("projects", "")
    listed = extract_skills(sections.get("skills", ""))
    unproven = [s for s in listed if not has_skill(evidence, s)]
    rules = [
        ("Generic objective statement", bool(re.search(r"seeking a? ?(challenging|good|suitable)|hard[- ]working|to work in a reputed", lowered)),
         "Replace it with one line naming your target role and strongest proof."),
        ("First-person wording", len(re.findall(r"\b(i|my|me)\b", lowered)) >= 3, "Start bullets with action verbs instead of I or my."),
        ("Passive 'responsible for' wording", lowered.count("responsible for") >= 2, "State what you did and the result."),
        ("Most listed skills have no proof", len(listed) >= 4 and len(unproven) / len(listed) > 0.6,
         "Show listed skills in a project or role: " + ", ".join(unproven[:4])),
        ("No dates found", not re.search(r"\b(19|20)\d{2}\b", resume), "Add dates to education, projects and experience."),
        ("Resume is very long", len(resume.split()) > 1200, "Cut to one page for campus roles."),
        ("Placeholder text", bool(re.search(r"lorem ipsum|\bxxx+\b|\btbd\b", lowered)), "Remove placeholder text."),
    ]
    return [{"flag": flag, "fix": fix} for flag, hit, fix in rules if hit]


def resume_score(resume: str, jd: str, role: str = "") -> dict:
    """Tool: score a resume with the fixed 100-point rubric. Same input, same score."""
    gap = keyword_gap(resume, jd)
    sections = parse_sections(resume)
    proof_text = sections.get("experience", "") + sections.get("projects", "")
    breakdown = []

    def add(name, score, why):
        breakdown.append({"criterion": name, "max": RUBRIC[name], "score": int(round(min(score, RUBRIC[name]))), "why": why})

    has_jd_skills = gap["jd_skill_count"] > 0
    if has_jd_skills:
        add("ATS keyword match", 30 * gap["coverage_pct"] / 100,
            f"{len(gap['matched'])} matched, {len(gap['partial'])} partial, {len(gap['missing'])} missing of {gap['jd_skill_count']} JD skills.")
        total_weight = sum(PRIORITY_WEIGHT[i["priority"]] for key in ("matched", "partial", "missing") for i in gap[key])
        proven = [i for i in gap["matched"] if has_skill(proof_text, i["skill"])]
        add("Skills alignment", 25 * sum(PRIORITY_WEIGHT[i["priority"]] for i in proven) / total_weight,
            f"{len(proven)} JD skills are proven in experience or projects, not just listed.")
    else:
        add("ATS keyword match", 15, "The JD names no recognised skills, so a neutral score was used.")
        add("Skills alignment", 12.5, "The JD names no recognised skills, so a neutral score was used.")

    role_tokens = {t for t in re.findall(r"[a-z]+", role.lower()) if t not in STOPWORDS}
    role_hits = sum(1 for t in role_tokens if t in resume.lower())
    role_points = 6 * role_hits / len(role_tokens) if role_tokens else 3
    proof_bullets = bullets(proof_text)
    bullet_points = min(len(proof_bullets), 6)
    jd_terms = [w for w, _ in Counter(w for w in re.findall(r"[a-z]{4,}", jd.lower()) if w not in STOPWORDS).most_common(20)]
    term_hits = sum(1 for w in jd_terms if w in proof_text.lower())
    term_points = 8 * term_hits / len(jd_terms) if jd_terms else 4
    add("Experience relevance", role_points + bullet_points + term_points,
        f"Role words {role_hits}/{len(role_tokens)}, {len(proof_bullets)} proof bullets, {term_hits}/{len(jd_terms)} JD terms in experience or projects.")

    checklist = formatting_checklist(resume)
    passed = sum(1 for c in checklist if c["passed"])
    add("Resume quality", 15 * passed / len(checklist), f"{passed} of {len(checklist)} formatting checks passed.")

    flags = red_flags(resume, gap)
    add("Red flags", max(0, 10 - 2 * len(flags)), f"{len(flags)} red flag(s), 2 points each.")

    confidence, reason = "High", "The JD names enough skills and the resume is readable."
    if gap["jd_skill_count"] < 3:
        confidence, reason = "Low", "The JD names fewer than 3 recognised skills."
    elif gap["jd_skill_count"] < 6 or len(resume.split()) < 150:
        confidence, reason = "Medium", "The JD or resume gives limited detail."
    return {
        "total": sum(b["score"] for b in breakdown),
        "breakdown": breakdown,
        "checklist": checklist,
        "red_flags": flags,
        "gap": gap,
        "confidence": confidence,
        "confidence_reason": reason,
    }


_EDITABLE = {"company", "role", "job_description", "status", "applied_on", "follow_up_on", "resume_score", "notes"}


def application_tracker(action: str, application_id: int | None = None, **fields) -> dict:
    """Tool: list, add, update or delete tracked applications."""
    action = action.lower()
    if action == "list":
        return {"applications": db.query("SELECT * FROM applications ORDER BY updated_at DESC, id DESC")}

    unknown = set(fields) - _EDITABLE
    if unknown:
        raise ValueError(f"Unknown fields: {sorted(unknown)}")
    status = fields.get("status")
    if status is not None:
        status = fields["status"] = status.upper()
        if status not in STATUSES:
            raise ValueError(f"Status must be one of {STATUSES}")

    if action == "add":
        company, role = (fields.get("company") or "").strip(), (fields.get("role") or "").strip()
        if not company or not role:
            raise ValueError("Company and role are required.")
        fields.update(company=company, role=role, status=status or "SAVED", updated_at=db.now())
        if fields["status"] == "APPLIED" and not fields.get("applied_on"):
            fields["applied_on"] = db.today().isoformat()
        columns = ", ".join(fields)
        new_id = db.execute(f"INSERT INTO applications ({columns}) VALUES ({', '.join('?' * len(fields))})", tuple(fields.values()))
        db.execute("INSERT INTO application_events (application_id, to_status, at) VALUES (?, ?, ?)", (new_id, fields["status"], db.now()))
        return _get(new_id)

    current = _get(application_id)
    if action == "delete":
        db.execute("DELETE FROM applications WHERE id = ?", (application_id,))
        return {"deleted": application_id}
    if action != "update":
        raise ValueError("Action must be list, add, update or delete.")
    if status == "APPLIED" and not current.get("applied_on") and not fields.get("applied_on"):
        fields["applied_on"] = db.today().isoformat()
    fields["updated_at"] = db.now()
    assignments = ", ".join(f"{key} = ?" for key in fields)
    db.execute(f"UPDATE applications SET {assignments} WHERE id = ?", (*fields.values(), application_id))
    if status and status != current["status"]:
        db.execute("INSERT INTO application_events (application_id, from_status, to_status, at) VALUES (?, ?, ?, ?)",
                   (application_id, current["status"], status, db.now()))
    return _get(application_id)


def _get(application_id) -> dict:
    rows = db.query("SELECT * FROM applications WHERE id = ?", (application_id,))
    if not rows:
        raise ValueError(f"Application {application_id} not found.")
    return rows[0]


def read_resume_file(filename: str, content: bytes) -> str:
    """Extract text from an uploaded PDF, DOCX or TXT resume."""
    name = filename.lower()
    if name.endswith(".pdf"):
        from pypdf import PdfReader
        return "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(content)).pages).strip()
    if name.endswith(".docx"):
        from docx import Document
        return "\n".join(p.text for p in Document(io.BytesIO(content)).paragraphs).strip()
    if name.endswith(".txt"):
        return content.decode("utf-8", errors="replace").strip()
    raise ValueError("Please upload a PDF, DOCX or TXT file.")

"""Decision tools: what-if simulator, skill roadmap, job matches, delivery analysis."""
import json
import re

from . import db, governance, memory, research
from .connector import search_postings_local
from .tools import RUBRIC, application_tracker, keyword_gap, resume_score
from .vocab import extract_skills, related_to

FILLERS = ["um", "uh", "basically", "actually", "literally", "you know", "kind of", "sort of", "i mean"]


def what_if(resume: str, jd: str, role: str = "", add_skills=(), fixes=()) -> dict:
    """Re-score the resume as if the selected improvements were really made."""
    base = resume_score(resume, jd, role)
    changed = resume
    if add_skills:
        names = ", ".join(add_skills)
        proof = "\n".join(f"- Built a project using {skill}." for skill in add_skills)
        changed = f"{resume}\n\nSKILLS\n{names}\n\nPROJECTS\n{proof}\n"
    result = resume_score(changed, jd, role)

    fixes = set(fixes)
    checklist = [{**c, "passed": c["passed"] or c["item"] in fixes} for c in result["checklist"]]
    flags = [f for f in result["red_flags"] if f["flag"] not in fixes]
    passed = sum(c["passed"] for c in checklist)
    replacements = {"Resume quality": round(RUBRIC["Resume quality"] * passed / len(checklist)),
                    "Red flags": max(0, RUBRIC["Red flags"] - 2 * len(flags))}
    before = {b["criterion"]: b["score"] for b in base["breakdown"]}
    parts = []
    for part in result["breakdown"]:
        score = replacements.get(part["criterion"], part["score"])
        parts.append({"criterion": part["criterion"], "max": part["max"], "before": before[part["criterion"]], "after": score})
    total = sum(p["after"] for p in parts)
    return {"before": base["total"], "after": total, "change": total - base["total"], "parts": parts,
            "note": "Estimate only. Add a skill or result to your resume only if it is true."}


def skill_roadmap(limit: int = 5) -> dict:
    """Rank skills to learn next by market demand, tracked jobs and ease."""
    profile = memory.get_profile()
    owned = set(profile["skills"]) | set(extract_skills(profile["resume_text"]))
    market = research.run(profile["target_roles"], sorted(owned))
    rejected = {f["skill"]: f["reason"] for f in memory.all_feedback() if f["decision"] == "rejected" and f["skill"]}
    apps = [a for a in application_tracker("list")["applications"] if a["job_description"] and a["status"] not in ("REJECTED", "WITHDRAWN")]
    needed = {}
    for app in apps:
        for item in keyword_gap(profile["resume_text"], app["job_description"])["missing"]:
            needed.setdefault(item["skill"], []).append(app["id"])

    postings = {}
    for role in profile["target_roles"] or [""]:
        for row in search_postings_local(role, "phrase" if role else "all", 300)["postings"]:
            for skill in extract_skills(f"{row['description']} {row['skills']}"):
                postings.setdefault(skill, []).append(row)

    items = []
    for row in market["top_skills"]:
        skill = row["skill"]
        if row["student_has"]:
            continue
        near = sorted(related_to(skill) & owned)
        app_share = len(needed.get(skill, [])) / len(apps) if apps else 0
        score = round(100 * (0.5 * row["pct"] / 100 + 0.35 * app_share + 0.15 * (1 if near else 0.4)))
        confidence = governance.confidence_for(market["sample_size"], row["count"], market["dataset"]["confidence_cap"])
        weeks = 1 if near else 2
        items.append({
            "skill": skill, "priority_score": score, "demand_pct": row["pct"], "postings": row["count"],
            "needed_by_applications": needed.get(skill, []), "related_skills_you_have": near,
            "effort": f"About {weeks} to {weeks + 1} weeks (estimate)", "confidence": confidence,
            "previously_rejected": rejected.get(skill),
            "citations": [research._citation(p) for p in postings.get(skill, [])[:3]],
            "plan": [f"Learn the core ideas of {skill}" + (f", building on {near[0]}" if near else ""),
                     f"Build one small project that uses {skill}", "Add honest proof to your resume",
                     f"Practise explaining {skill} and its trade-offs"],
        })
    items.sort(key=lambda i: (-i["priority_score"], i["skill"]))
    return {"items": items[:limit], "dataset": market["dataset"], "sample_size": market["sample_size"],
            "method": "Priority = 50% market demand + 35% share of tracked jobs needing it + 15% ease from related skills."}


def job_matches(limit: int = 6) -> dict:
    """Find postings closest to the student's resume that are not tracked yet."""
    profile = memory.get_profile()
    tracked = {(a["company"].lower(), a["role"].lower()) for a in application_tracker("list")["applications"]}
    targets = [r.lower() for r in profile["target_roles"]]
    matches = []
    for post in search_postings_local("", "all", 400)["postings"]:
        if (post["company"].lower(), post["title"].lower()) in tracked:
            continue
        gap = keyword_gap(profile["resume_text"], f"{post['description']}\n{post['skills']}")
        if gap["jd_skill_count"] < 3:
            continue
        matches.append({
            "posting_id": post["id"], "title": post["title"], "company": post["company"], "location": post["location"],
            "posted_on": post["posted_on"], "source": post["source"], "source_row": post["source_row"], "description": post["description"],
            "match_pct": gap["coverage_pct"], "target_role": any(t in post["title"].lower() for t in targets),
            "matched": [i["skill"] for i in gap["matched"]], "missing": [i["skill"] for i in gap["missing"]],
        })
    matches.sort(key=lambda m: (-m["target_role"], -m["match_pct"], -(m["posted_on"] is not None), m["posting_id"]))
    return {"items": matches[:limit], "dataset": governance.dataset_info()}


def delivery(answer: str, seconds: float | None = None) -> dict:
    """Rule-based speaking and writing signals for a mock answer."""
    lowered = f" {re.sub(r'[^a-z ]', ' ', answer.lower())} "
    lowered = re.sub(r"\s+", " ", lowered)
    fillers = {word: lowered.count(f" {word} ") for word in FILLERS if lowered.count(f" {word} ")}
    words = len(answer.split())
    sentences = max(1, len(re.findall(r"[.!?]+", answer)))
    pace = round(words / (seconds / 60)) if seconds and seconds >= 5 else None
    tips = []
    if sum(fillers.values()) >= 3:
        tips.append("Replace filler words with a short pause.")
    if pace and pace > 170:
        tips.append("Slow down a little so each point lands.")
    if pace and pace < 100:
        tips.append("Try a steadier pace with fewer long pauses.")
    if words / sentences > 28:
        tips.append("Use shorter sentences.")
    return {"words": words, "words_per_minute": pace, "filler_count": sum(fillers.values()), "fillers": fillers,
            "average_sentence_words": round(words / sentences), "tips": tips}


def readiness_history() -> list[dict]:
    rows = db.query("SELECT id, data, created_at FROM reports ORDER BY id")
    return [{"report_id": r["id"], "at": r["created_at"], "score": json.loads(r["data"])["readiness"]["score"]} for r in rows]

"""Long-term profile and the retrieval store of accepted or rejected advice."""
import json
import math
import re
from collections import Counter

from . import db
from .vocab import canonical

EMPTY_PROFILE = {
    "name": "", "education": "", "graduation_year": "", "target_roles": [], "skills": [],
    "weak_areas": [], "resume_text": "",
}


def get_profile() -> dict:
    rows = db.query("SELECT data FROM profile WHERE id = 1")
    return {**EMPTY_PROFILE, **(json.loads(rows[0]["data"]) if rows else {})}


def save_profile(data: dict) -> dict:
    profile = {**get_profile(), **{k: v for k, v in data.items() if k in EMPTY_PROFILE}}
    profile["skills"] = sorted({canonical(s) for s in profile["skills"] if s.strip()})
    db.execute(
        "INSERT INTO profile (id, data, updated_at) VALUES (1, ?, ?) "
        "ON CONFLICT(id) DO UPDATE SET data = excluded.data, updated_at = excluded.updated_at",
        (json.dumps(profile), db.now()),
    )
    return profile


def add_feedback(suggestion: str, decision: str, skill: str = "", reason: str = "", context: str = "") -> dict:
    if decision not in ("accepted", "rejected"):
        raise ValueError("Decision must be accepted or rejected.")
    new_id = db.execute(
        "INSERT INTO feedback (suggestion, skill, decision, reason, context, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (suggestion, skill, decision, reason, context, db.now()),
    )
    return db.query("SELECT * FROM feedback WHERE id = ?", (new_id,))[0]


def all_feedback() -> list[dict]:
    return db.query("SELECT * FROM feedback ORDER BY id DESC")


def _vector(text: str) -> Counter:
    return Counter(re.findall(r"[a-z0-9+#]{2,}", text.lower()))


def similarity(a: str, b: str) -> float:
    va, vb = _vector(a), _vector(b)
    dot = sum(va[t] * vb[t] for t in va.keys() & vb.keys())
    size = math.sqrt(sum(v * v for v in va.values())) * math.sqrt(sum(v * v for v in vb.values()))
    return dot / size if size else 0.0


def retrieve_feedback(suggestion: str, skill: str = "", min_similarity: float = 0.75) -> dict | None:
    """Find the closest past decision. Advice about a different skill never matches."""
    best, best_score = None, 0.0
    for item in all_feedback():
        if skill and item["skill"] and item["skill"] != skill:
            continue
        score = 1.0 if skill and item["skill"] == skill else similarity(suggestion, item["suggestion"])
        if score > best_score:
            best, best_score = item, score
    return {**best, "similarity": round(best_score, 2)} if best and best_score >= min_similarity else None

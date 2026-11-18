"""QA pass. Every rule here is code, so it cannot be talked out of by a model."""
import re
from datetime import date

from . import config, db
from .vocab import extract_skills, has_skill

HONESTY_NOTE = "Add this only if you have really used it. Otherwise, learn it first."
LOW_LABEL = "LOW CONFIDENCE"
WELL_KNOWN_COMPANIES = (
    "Google Microsoft Amazon Meta Apple Netflix Infosys TCS Wipro Accenture Cognizant Capgemini Deloitte IBM Oracle "
    "Flipkart Swiggy Zomato Paytm Adobe Salesforce Uber Intel Nvidia HCL Goldman".split()
)
COMPANY_SUFFIX = re.compile(r"\b[A-Z][\w&]*(?:\s[A-Z][\w&]*)*\s(?:Inc|Ltd|LLC|LLP|Corp|Pvt|Technologies|Solutions|Labs|Systems)\b")


def dataset_info() -> dict:
    row = db.query(
        "SELECT COUNT(*) AS n, MAX(posted_on) AS newest, MIN(posted_on) AS oldest, MAX(is_demo) AS demo FROM postings"
    )[0]
    sources = [r["source"] for r in db.query("SELECT DISTINCT source FROM postings ORDER BY source")]
    cap, note = "High", ""
    if row["demo"]:
        cap, note = "Medium", "Demo data is synthetic, so it cannot support a High confidence claim or describe the real market."
    elif not row["newest"]:
        cap, note = "Medium", "The dataset has no posting dates, so recency cannot be checked."
    else:
        try:
            age = (db.today() - date.fromisoformat(row["newest"])).days
        except ValueError:
            age = None
        if age is None:
            cap, note = "Medium", "The dataset's dates could not be read."
        elif age > config.STALE_AFTER_DAYS:
            cap, note = "Low", f"The newest posting is {age} days old, so it may not reflect this year's market."
    return {"postings": row["n"], "newest": row["newest"], "oldest": row["oldest"], "is_demo": bool(row["demo"]),
            "sources": sources, "confidence_cap": cap, "note": note}


def confidence_for(sample: int, support: int, cap: str = "High") -> str:
    level = "Low"
    if support >= config.MIN_SUPPORTING_POSTINGS:
        if sample >= config.HIGH_CONFIDENCE_SAMPLE:
            level = "High"
        elif sample >= config.MEDIUM_CONFIDENCE_SAMPLE:
            level = "Medium"
    order = ["Low", "Medium", "High"]
    return order[min(order.index(level), order.index(cap))]


def label(text: str, confidence: str) -> str:
    return f"[{LOW_LABEL}] {text}" if confidence == "Low" and LOW_LABEL not in text else text


def verify_market_claims(claims: list[dict], cap: str = "High") -> tuple[list[dict], list[dict]]:
    """Keep only claims whose citations exist and really mention the skill."""
    kept, removed = [], []
    for claim in claims:
        citations = claim.get("citations") or []
        if not citations:
            removed.append({**claim, "qa_reason": "No citation"})
            continue
        ids = [c.get("posting_id") for c in citations]
        marks = ",".join("?" * len(ids))
        rows = {r["id"]: r for r in db.query(f"SELECT * FROM postings WHERE id IN ({marks})", tuple(ids))}
        if len(rows) != len(set(ids)):
            removed.append({**claim, "qa_reason": "Cites a posting that does not exist"})
            continue
        skill = claim.get("skill")
        if skill and not all(has_skill(f"{r['description']} {r['skills']}", skill) for r in rows.values()):
            removed.append({**claim, "qa_reason": "A cited posting does not mention the skill"})
            continue
        confidence = confidence_for(claim.get("sample_size", 0), claim.get("support", 0), cap)
        order = ["Low", "Medium", "High"]
        if claim.get("max_confidence"):
            confidence = order[min(order.index(confidence), order.index(claim["max_confidence"]))]
        kept.append({**claim, "confidence": confidence, "text": label(claim["text"], confidence), "qa": "passed"})
    return kept, removed


def check_narrative(text: str, facts: str, allowed_companies=()) -> list[str]:
    """Return problems found in model-written text. An empty list means it is safe."""
    problems = []
    allowed_numbers = set(re.findall(r"\d+(?:\.\d+)?", facts))
    invented = [n for n in re.findall(r"\d+(?:\.\d+)?", text) if n not in allowed_numbers]
    if invented:
        problems.append(f"Numbers not in the evidence: {sorted(set(invented))}")
    allowed = " ".join(allowed_companies).lower() + " " + facts.lower()
    names = [n for n in WELL_KNOWN_COMPANIES if re.search(rf"\b{n}\b", text) and n.lower() not in allowed]
    names += [m.group(0) for m in COMPANY_SUFFIX.finditer(text) if m.group(0).lower() not in allowed]
    if names:
        problems.append(f"Company names not in the evidence: {sorted(set(names))}")
    return problems


def check_rewrite(original: str, rewrite: str) -> list[str]:
    problems = []
    added = set(extract_skills(rewrite)) - set(extract_skills(original))
    if added:
        problems.append(f"Adds skills: {sorted(added)}")
    new_numbers = set(re.findall(r"\d+(?:\.\d+)?", rewrite)) - set(re.findall(r"\d+(?:\.\d+)?", original))
    if new_numbers:
        problems.append(f"Adds numbers: {sorted(new_numbers)}")
    return problems


def qa_recommendations(recommendations: list[dict]) -> list[dict]:
    out = []
    for rec in recommendations:
        rec = dict(rec)
        if rec.get("type") == "add_skill" and HONESTY_NOTE not in rec["text"]:
            rec["text"] = f"{rec['text']} {HONESTY_NOTE}"
        rec["text"] = label(rec["text"], rec.get("confidence", "Medium"))
        out.append(rec)
    return out


def qa_report(report: dict) -> list[dict]:
    """Final checklist shown to the student with the weekly report."""
    market = report["market"]["claims"]
    actions = report["actions"]
    low_ok = all(LOW_LABEL in c["text"] for c in market if c["confidence"] == "Low")
    _, failed = verify_market_claims(market, report["market"]["dataset"]["confidence_cap"])
    removed_earlier = len(report["market"].get("removed_claims", []))
    checks = [
        ("Every market claim has a source", all(c.get("citations") for c in market), f"{len(market)} claims checked"),
        ("Every citation exists and mentions the skill", not failed, f"{len(failed)} failed now, {removed_earlier} removed earlier"),
        ("Low-confidence claims are labelled", low_ok, "Label text: " + LOW_LABEL),
        ("Every action states its basis", all(a.get("basis") for a in actions), f"{len(actions)} actions checked"),
        ("Summary uses only verified facts", not report.get("summary_problems"), report.get("summary_source", "")),
        ("Data limits are disclosed", bool(report["market"]["dataset"]["sources"]), report["market"]["dataset"]["note"] or "No data warning"),
    ]
    return [{"check": name, "passed": bool(passed), "detail": detail} for name, passed, detail in checks]

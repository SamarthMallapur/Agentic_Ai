"""Deep-research loop: search -> extract -> compare -> synthesize."""
from collections import defaultdict

from . import config, governance
from .connector import DirectConnector
from .vocab import extract_skills


def _citation(posting: dict) -> dict:
    return {
        "posting_id": posting["id"], "title": posting["title"], "company": posting["company"],
        "posted_on": posting["posted_on"], "source": posting["source"], "source_row": posting["source_row"],
    }


def search(connector, roles: list[str], trace: list[dict]) -> dict[int, dict]:
    """Widen the search in rounds until there is enough evidence."""
    found: dict[int, dict] = {}
    roles = roles or [""]
    for round_no, mode in enumerate(["phrase", "tokens", "all"], start=1):
        for role in roles if mode != "all" else [""]:
            for posting in connector.call("search_postings", query=role, mode=mode, limit=300)["postings"]:
                found[posting["id"]] = posting
        trace.append({"step": "search", "round": round_no, "mode": mode, "postings_found": len(found)})
        if len(found) >= config.MIN_RESEARCH_SAMPLE:
            break
    return found


def extract(postings: dict[int, dict]) -> dict[str, list[dict]]:
    by_skill = defaultdict(list)
    for posting in postings.values():
        for skill in extract_skills(f"{posting['description']} {posting['skills']}"):
            by_skill[skill].append(posting)
    return by_skill


def compare(by_skill, sample: int, student_skills: set[str]) -> list[dict]:
    rows = []
    for skill, postings in by_skill.items():
        rows.append({
            "skill": skill, "count": len(postings), "pct": round(100 * len(postings) / sample),
            "student_has": skill in student_skills, "postings": postings,
        })
    return sorted(rows, key=lambda r: (-r["count"], r["skill"]))


def trends(rows: list[dict], postings: dict[int, dict]) -> list[dict]:
    """Compare the older and newer halves of the dated sample."""
    dated = sorted(p["posted_on"] for p in postings.values() if p["posted_on"])
    if len(dated) < 20 or dated[0] == dated[-1]:
        return []
    midpoint = dated[len(dated) // 2]
    older = sum(1 for d in dated if d < midpoint)
    newer = len(dated) - older
    if not older or not newer:
        return []
    out = []
    for row in rows:
        new = sum(1 for p in row["postings"] if p["posted_on"] and p["posted_on"] >= midpoint)
        old = sum(1 for p in row["postings"] if p["posted_on"] and p["posted_on"] < midpoint)
        delta = round(100 * new / newer) - round(100 * old / older)
        if delta >= 10 and new >= config.MIN_SUPPORTING_POSTINGS:
            out.append({**row, "delta": delta, "older_pct": round(100 * old / older), "newer_pct": round(100 * new / newer),
                        "older_n": older, "newer_n": newer, "midpoint": midpoint,
                        "recent": [p for p in row["postings"] if p["posted_on"] and p["posted_on"] >= midpoint]})
    return sorted(out, key=lambda r: -r["delta"])[:3]


def synthesize(rows, rising, sample: int, scope: str) -> list[dict]:
    claims = []

    def add(kind, skill, text, evidence, support, citing, sample_size=sample, max_confidence=None):
        claims.append({
            "id": f"M{len(claims) + 1}", "kind": kind, "skill": skill, "text": text, "evidence": evidence,
            "support": support, "sample_size": sample_size, "max_confidence": max_confidence,
            "citations": [_citation(p) for p in citing[:3]],
        })

    for row in rows[:8]:
        add("demand", row["skill"], f"{row['skill']} appears in {row['pct']}% of {scope} postings.",
            f"{row['count']} of {sample} postings mention {row['skill']}.", row["count"], row["postings"])
    for row in [r for r in rows if not r["student_has"]][:3]:
        add("gap", row["skill"], f"{row['skill']} is in demand ({row['pct']}%) but is not on your profile.",
            f"{row['count']} of {sample} postings mention it. Your profile does not list it.", row["count"], row["postings"])
    for row in rising:
        add("rising", row["skill"], f"{row['skill']} mentions rose from {row['older_pct']}% to {row['newer_pct']}% of {scope} postings.",
            f"Before {row['midpoint']}: {row['older_pct']}% of {row['older_n']}. From {row['midpoint']}: {row['newer_pct']}% of {row['newer_n']}.",
            len(row["recent"]), row["recent"], min(row["older_n"], row["newer_n"]), "Medium")
    return claims


class _Trace(list):
    """A trace list that can report each step as it happens."""

    def __init__(self, on_step=None):
        super().__init__()
        self.on_step = on_step

    def append(self, step):
        super().append(step)
        if self.on_step:
            self.on_step(step)


def run(roles: list[str], student_skills: list[str], connector=None, on_step=None) -> dict:
    connector = connector or DirectConnector()
    trace = _Trace(on_step)
    dataset = connector.call("get_dataset_info")
    postings = search(connector, roles, trace)
    sample = len(postings)
    scope = " / ".join(roles) if roles and trace[-1]["mode"] != "all" else "all"
    by_skill = extract(postings)
    trace.append({"step": "extract", "skills_found": len(by_skill), "postings_read": sample})
    rows = compare(by_skill, sample, set(student_skills)) if sample else []
    trace.append({"step": "compare", "skills_on_profile": sum(r["student_has"] for r in rows)})
    rising = trends(rows, postings)
    claims = synthesize(rows, rising, sample, scope)
    kept, removed = governance.verify_market_claims(claims, dataset["confidence_cap"])
    trace.append({"step": "synthesize", "claims": len(claims), "claims_after_qa": len(kept)})

    top = rows[:10]
    roles_count = defaultdict(int)
    for posting in postings.values():
        roles_count[posting["title"]] += 1
    return {
        "scope": scope, "sample_size": sample, "dataset": dataset, "transport": connector.transport,
        "research_trace": trace, "claims": kept, "removed_claims": removed,
        "top_skills": [{k: r[k] for k in ("skill", "count", "pct", "student_has")} for r in rows[:15]],
        "top_roles": sorted(([t, c] for t, c in roles_count.items()), key=lambda x: -x[1])[:6],
        "coverage_pct": round(100 * sum(r["student_has"] for r in top) / len(top)) if top else None,
    }

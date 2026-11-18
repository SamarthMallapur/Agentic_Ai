"""Weekly report: a swarm of three agents, merged and passed through QA."""
import json
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date

from . import agents, db, governance, llm, memory, prompts, research
from .connector import DirectConnector, MCPConnector
from .tools import ACTIVE_STATUSES, application_tracker


def readiness(review_avg, coverage, interview_avg, active_apps) -> dict:
    """Readiness from real data. Missing parts are left out, never guessed."""
    parts = [
        ("Resume match", 40, review_avg),
        ("Market skill coverage", 30, coverage),
        ("Interview practice", 20, interview_avg * 10 if interview_avg is not None else None),
        ("Application activity", 10, min(active_apps, 5) * 20),
    ]
    known = [(name, weight, value) for name, weight, value in parts if value is not None]
    weight_total = sum(w for _, w, _ in known)
    score = round(sum(w * v for _, w, v in known) / weight_total) if weight_total else 0
    return {
        "score": score,
        "parts": [{"name": n, "weight": w, "value": None if v is None else round(v)} for n, w, v in parts],
        "missing": [n for n, _, v in parts if v is None],
    }


def tracker_summary() -> dict:
    apps = application_tracker("list")["applications"]
    counts = {}
    for app in apps:
        counts[app["status"]] = counts.get(app["status"], 0) + 1
    today = db.today().isoformat()
    overdue = [a for a in apps if a["follow_up_on"] and a["follow_up_on"] <= today and a["status"] in ACTIVE_STATUSES]
    return {
        "total": len(apps), "by_status": counts, "active": sum(1 for a in apps if a["status"] in ACTIVE_STATUSES),
        "follow_ups_due": [{"id": a["id"], "company": a["company"], "role": a["role"], "due": a["follow_up_on"]} for a in overdue],
    }


def dashboard() -> dict:
    profile = memory.get_profile()
    tracker = tracker_summary()
    review = agents.reviewer_worker()
    coach = agents.coach_worker()
    market = research.run(profile["target_roles"], profile["skills"], DirectConnector())
    return {
        "student": profile["name"], "tracker": tracker, "coach": coach,
        "readiness": readiness(review.get("average"), market["coverage_pct"], coach["average"], tracker["active"]),
        "resume_average": review.get("average"), "dataset": market["dataset"],
        "top_gap": next((c for c in market["claims"] if c["kind"] == "gap"), None),
    }


def _plan(review: dict, coach: dict, market: dict, tracker: dict) -> list[dict]:
    rejected = {f["skill"]: f for f in memory.all_feedback() if f["decision"] == "rejected" and f["skill"]}
    actions = []
    for follow_up in tracker["follow_ups_due"][:2]:
        actions.append({"action": f"Follow up on {follow_up['role']} at {follow_up['company']}.", "why": f"Follow-up was due on {follow_up['due']}.",
                        "basis": f"Tracker application #{follow_up['id']}", "confidence": "High"})
    gap_claims = [c for c in market["claims"] if c["kind"] == "gap"]
    for claim in gap_claims:
        if claim["skill"] in rejected:
            continue
        actions.append({"action": f"Learn {claim['skill']} and build one small project with it.", "why": claim["text"],
                        "basis": f"Market claim {claim['id']}", "confidence": claim["confidence"]})
        break
    if review.get("common_missing"):
        item = next((m for m in review["common_missing"] if m["skill"] not in rejected), None)
        if item:
            ids = ", ".join(f"#{i}" for i in item["application_ids"])
            actions.append({"action": f"Close the {item['skill']} gap for your tracked roles.", "why": f"It is missing for {len(item['application_ids'])} tracked application(s).",
                            "basis": f"Rubric review of applications {ids}", "confidence": "Medium"})
    if review.get("weakest_criterion"):
        actions.append({"action": f"Improve your resume's {review['weakest_criterion'].lower()}.", "why": "It is your lowest rubric area across tracked roles.",
                        "basis": "Fixed rubric results", "confidence": "Medium"})
    if coach["weak_categories"]:
        actions.append({"action": f"Practise {coach['weak_categories'][0]} interview answers.", "why": f"Average {coach['by_category'][coach['weak_categories'][0]]}/10 in this category.",
                        "basis": f"{coach['attempts']} mock answer(s)", "confidence": coach["confidence"]})
    elif not coach["attempts"]:
        actions.append({"action": "Answer one mock interview question.", "why": "There is no practice data yet.", "basis": "Interview history is empty", "confidence": "High"})
    return [{**a, "action": governance.label(a["action"], a["confidence"])} for a in actions[:5]]


def _evidence_table(report: dict) -> list[dict]:
    rows = []
    for claim in report["market"]["claims"]:
        refs = "; ".join(f"Posting #{c['posting_id']} ({c['source']} row {c['source_row']})" for c in claim["citations"])
        rows.append({"id": claim["id"], "claim": claim["text"], "evidence": claim["evidence"], "source": refs,
                     "sample": claim["sample_size"], "confidence": claim["confidence"], "qa": "Citation verified"})
    for item in report["resume"].get("reviewed", []):
        rows.append({"id": f"R{item['application_id']}", "claim": f"Resume scores {item['score']}/100 for {item['role']} at {item['company']}.",
                     "evidence": "Fixed 100-point rubric", "source": f"Tracker application #{item['application_id']} job description", "sample": 1,
                     "confidence": item["confidence"], "qa": "Recomputed this run"})
    if report["interview"]["attempts"]:
        interview = report["interview"]
        rows.append({"id": "I1", "claim": f"Average mock interview score is {interview['average']}/10.", "evidence": f"{interview['attempts']} saved answer(s)",
                     "source": "Interview attempts " + ", ".join(f"#{i}" for i in interview["attempt_ids"]), "sample": interview["attempts"],
                     "confidence": interview["confidence"], "qa": "Computed from saved attempts"})
    return rows


def _summary(report: dict) -> None:
    top = report["actions"][0]["action"] if report["actions"] else "Keep your tracker up to date."
    resume_avg = report["resume"].get("average")
    default = (f"Your readiness is {report['readiness']['score']}/100 from the data available. You have {report['applications']['active']} active "
               f"application(s)" + (f" and an average resume match of {resume_avg}/100" if resume_avg is not None else "") + f". Next step: {top}")
    facts = json.dumps({
        "readiness": report["readiness"]["score"], "applications": report["applications"], "resume_average": resume_avg,
        "interview": report["interview"].get("average"), "market_claims": [c["text"] for c in report["market"]["claims"][:6]],
        "actions": [a["action"] for a in report["actions"]],
    })
    text = llm.generate("weekly_summary", prompts.WEEKLY_SUMMARY.format(facts=facts), temperature=0.2)
    report["summary"], report["summary_source"], report["summary_problems"] = default, "Template from verified facts", []
    if text:
        problems = governance.check_narrative(text, facts + default)
        if problems:
            report["summary_source"] = "Template used because AI text failed QA: " + "; ".join(problems)
        else:
            report["summary"], report["summary_source"] = text, "Gemini, numbers and company names checked by QA"


def to_markdown(r: dict) -> str:
    market = r["market"]
    lines = [f"# Weekly Placement Readiness Report", "", f"**Student:** {r['student']}  ", f"**Generated:** {r['generated_at']}  ",
             f"**Readiness:** {r['readiness']['score']}/100", ""]
    if market["dataset"]["note"]:
        lines += [f"> **Data notice:** {market['dataset']['note']}", ""]
    lines += ["## Summary", r["summary"], "", "## Recommended actions"]
    lines += [f"{i}. **{a['action']}** {a['why']} _Basis: {a['basis']}. Confidence: {a['confidence']}._" for i, a in enumerate(r["actions"], 1)]
    lines += ["", "## Applications", f"{r['applications']['total']} tracked, {r['applications']['active']} active. "
              + ", ".join(f"{k}: {v}" for k, v in r["applications"]["by_status"].items()), "", "## Resume-Reviewer"]
    if r["resume"].get("reviewed"):
        lines += ["| Application | Score | Confidence |", "|---|---:|---|"]
        lines += [f"| #{i['application_id']} {i['role']} at {i['company']} | {i['score']}/100 | {i['confidence']} |" for i in r["resume"]["reviewed"]]
    else:
        lines.append(r["resume"].get("note", ""))
    interview = r["interview"]
    lines += ["", "## Interview-Coach", (f"{interview['attempts']} answer(s), average {interview['average']}/10. Confidence: {interview['confidence']}."
                                         if interview["attempts"] else interview["note"]),
              "", "## Market-Analyst", f"Scope: {market['scope']}. Sample: {market['sample_size']} postings. Connector: {market['transport']}.", ""]
    lines += [f"- {c['text']} [{c['id']}] _Confidence: {c['confidence']}._" for c in market["claims"]]
    lines += ["", "## Evidence table", "| ID | Claim | Evidence | Source | n | Confidence |", "|---|---|---|---|---:|---|"]
    lines += [f"| {e['id']} | {e['claim']} | {e['evidence']} | {e['source']} | {e['sample']} | {e['confidence']} |" for e in r["evidence_table"]]
    lines += ["", "## QA checks"] + [f"- {'PASS' if q['passed'] else 'FAIL'}: {q['check']} ({q['detail']})" for q in r["qa"]]
    return "\n".join(lines) + "\n"


def weekly_report(on_event=None) -> dict:
    """Run the swarm. on_event receives live progress for the mission-control view."""
    trace, started = [], time.perf_counter()
    emit = on_event or (lambda event: None)

    def run_node(name, fn):
        begin = time.perf_counter()
        emit({"type": "node", "node": name, "state": "running"})
        try:
            return fn()
        finally:
            ms = round(1000 * (time.perf_counter() - begin))
            trace.append({"node": name, "ms": ms})
            emit({"type": "node", "node": name, "state": "done", "ms": ms})

    profile = run_node("Load memory", memory.get_profile)
    connector = MCPConnector()
    with ThreadPoolExecutor(max_workers=3) as pool:
        review_job = pool.submit(run_node, "Resume-Reviewer", agents.reviewer_worker)
        coach_job = pool.submit(run_node, "Interview-Coach", agents.coach_worker)
        market_job = pool.submit(run_node, "Market-Analyst (research loop)",
                                 lambda: research.run(profile["target_roles"], profile["skills"], connector,
                                                      lambda step: emit({"type": "research", **step})))
        review, coach, market = review_job.result(), coach_job.result(), market_job.result()

    def merge():
        tracker = tracker_summary()
        report = {
            "student": profile["name"] or "Student", "generated_at": db.now(), "week_of": date.today().isocalendar()[1],
            "applications": tracker, "resume": review, "interview": coach, "market": market,
            "readiness": readiness(review.get("average"), market["coverage_pct"], coach["average"], tracker["active"]),
            "actions": _plan(review, coach, market, tracker),
        }
        report["evidence_table"] = _evidence_table(report)
        return report

    report = run_node("Merge", merge)
    run_node("Write summary", lambda: _summary(report))
    report["qa"] = run_node("QA gate", lambda: governance.qa_report(report))
    report["qa_passed"] = all(q["passed"] for q in report["qa"])
    report["trace"] = trace + [{"node": "Total", "ms": round(1000 * (time.perf_counter() - started))}]
    markdown = to_markdown(report)
    report["id"] = db.execute("INSERT INTO reports (data, markdown, created_at) VALUES (?, ?, ?)", (json.dumps(report), markdown, db.now()))
    return report


def latest_report() -> dict | None:
    rows = db.query("SELECT id, data FROM reports ORDER BY id DESC LIMIT 1")
    return {**json.loads(rows[0]["data"]), "id": rows[0]["id"]} if rows else None

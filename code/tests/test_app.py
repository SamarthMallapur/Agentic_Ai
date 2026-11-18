import re

import pytest
from fastapi.testclient import TestClient

from app import agents, config, db, governance, llm, memory, orchestrator, research, tools
from app.connector import MCPConnector
from app.vocab import extract_skills


def text(folder, name):
    return (folder / name).read_text(encoding="utf-8")


RESUME = text(config.DEMO_RESUMES, "backend_student.txt")
JD = text(config.DEMO_JDS, "backend_developer.txt")


def test_vocabulary_avoids_false_matches():
    assert "Java" not in extract_skills("JavaScript only")
    assert "REST APIs" not in extract_skills("the rest of the team")
    assert "C++" in extract_skills("Strong C++ skills")


def test_score_is_repeatable_and_adds_up():
    first, second = tools.resume_score(RESUME, JD, "Backend Developer"), tools.resume_score(RESUME, JD, "Backend Developer")
    assert first == second
    assert first["total"] == sum(b["score"] for b in first["breakdown"])
    assert [b["max"] for b in first["breakdown"]] == list(tools.RUBRIC.values())


def test_skill_file_matches_code_rubric():
    skill = config.SKILL_FILE.read_text(encoding="utf-8")
    for name, points in tools.RUBRIC.items():
        assert re.search(rf"\| {name} \| {points} \|", skill)


def test_strong_resume_beats_weak_resume():
    weak = text(config.DEMO_RESUMES, "weak_resume.txt")
    assert tools.resume_score(RESUME, JD, "Backend Developer")["total"] > tools.resume_score(weak, JD, "Backend Developer")["total"] + 20


def test_gap_finds_missing_required_skill():
    missing = {i["skill"]: i["priority"] for i in tools.keyword_gap(RESUME, JD)["missing"]}
    assert missing["Docker"] == "HIGH"


def test_intake_asks_before_reviewing(demo):
    assert agents.review_resume("too short", JD)["status"] == "needs_input"
    thin_jd = "Python developer needed for our growing team today, please apply soon if this role sounds right for you"
    result = agents.review_resume(RESUME, thin_jd, "", "")
    assert result["status"] == "needs_input" and result["can_continue"]
    forced = agents.review_resume(RESUME, thin_jd, "", "", continue_anyway=True)
    assert forced["status"] == "done" and forced["confidence"] == "Low"


def test_skill_advice_is_honest_and_rejected_advice_is_hidden(demo):
    memory.add_feedback("Add Docker", "rejected", "Docker", "Never used it")
    result = agents.review_resume(RESUME, JD, "Demo Company 01", "Backend Developer")
    assert "Docker" in [r["skill"] for r in result["hidden_by_memory"]]
    assert "Docker" not in [r["skill"] for r in result["recommendations"]]
    assert "AWS" in [r["skill"] for r in result["recommendations"]]  # Similar wording, different skill.
    assert all(governance.HONESTY_NOTE in r["text"] for r in result["recommendations"] if r["type"] == "add_skill")


def test_tracker_add_update_delete_and_validation(demo):
    app = tools.application_tracker("add", company="X", role="Y")
    assert tools.application_tracker("update", app["id"], status="applied")["applied_on"]
    with pytest.raises(ValueError):
        tools.application_tracker("update", app["id"], status="NOPE")
    with pytest.raises(ValueError):
        tools.application_tracker("add", company="X", role="Y", **{"id; DROP TABLE": 1})
    assert len(db.query("SELECT * FROM application_events WHERE application_id = ?", (app["id"],))) == 2
    tools.application_tracker("delete", app["id"])


def test_research_widens_until_enough_evidence(demo):
    result = research.run(["Backend Developer"], ["Python"])
    assert [t["round"] for t in result["research_trace"] if t["step"] == "search"] == [1]
    narrow = research.run(["Nonexistent Role"], [])
    assert narrow["research_trace"][2]["mode"] == "all"


def test_every_market_claim_is_cited_and_demo_is_capped(demo):
    result = research.run(["Backend Developer"], ["Python"])
    assert result["claims"]
    assert all(c["citations"] and c["confidence"] != "High" for c in result["claims"])


@pytest.mark.parametrize("citations,reason", [([], "No citation"), ([{"posting_id": 999999}], "does not exist")])
def test_qa_removes_bad_citations(demo, citations, reason):
    kept, removed = governance.verify_market_claims([{"text": "x", "skill": "Python", "sample_size": 200, "support": 50, "citations": citations}])
    assert not kept and reason in removed[0]["qa_reason"]


def test_qa_removes_citation_that_does_not_support_claim(demo):
    posting = db.query("SELECT id FROM postings WHERE description NOT LIKE '%Rust%' LIMIT 1")[0]
    kept, removed = governance.verify_market_claims([{"text": "Rust", "skill": "Rust", "sample_size": 200, "support": 50, "citations": [{"posting_id": posting["id"]}]}])
    assert not kept and removed


def test_low_confidence_is_labelled(demo):
    posting = db.query("SELECT id FROM postings WHERE description LIKE '%Python%' LIMIT 1")[0]
    kept, _ = governance.verify_market_claims([{"text": "Python is common", "skill": "Python", "sample_size": 5, "support": 2, "citations": [{"posting_id": posting["id"]}]}])
    assert kept[0]["confidence"] == "Low" and governance.LOW_LABEL in kept[0]["text"]


def test_narrative_and_rewrite_guards():
    assert governance.check_narrative("Google is hiring 90% more people.", "Python 40")
    assert not governance.check_narrative("Python appears in 40% of postings.", "Python 40")
    assert governance.check_rewrite("Built an API", "Built a Docker API serving 500 users")
    assert not governance.check_rewrite("Built an API", "Built an API for internal users")


def test_contact_details_are_redacted():
    cleaned = llm.redact("Mail a.b@example.com or call +91 90000 00000")
    assert "example.com" not in cleaned and "90000" not in cleaned


def test_interview_works_without_ai(demo):
    questions = agents.interview_questions(JD, "Backend Developer")["questions"]
    assert {q["category"] for q in questions} == {"Technical", "Project", "Behavioral", "Resume", "Weakness"}
    result = agents.evaluate_answer(questions[0], "First I would explain the idea, then give an example from my project with 2 tables.")
    assert result["confidence"] == "Low" and governance.LOW_LABEL in result["note"]


def test_mcp_connector_really_uses_mcp(demo):
    connector = MCPConnector()
    result = connector.call("search_postings", query="Backend Developer", mode="phrase", limit=5)
    assert result["count"] == 5 and connector.transport == "mcp-stdio"


def test_weekly_report_end_to_end(demo):
    report = orchestrator.weekly_report()
    assert report["qa_passed"] and report["market"]["transport"] == "mcp-stdio"
    assert {t["node"] for t in report["trace"]} >= {"Resume-Reviewer", "Interview-Coach", "Market-Analyst (research loop)", "Merge", "QA gate"}
    assert all(a["basis"] for a in report["actions"])
    assert "Kubernetes" not in " ".join(a["action"] for a in report["actions"] if a["action"].startswith("Learn"))
    assert orchestrator.latest_report()["id"] == report["id"]


def test_readiness_is_computed_not_fixed():
    assert orchestrator.readiness(50, 50, 5, 5)["score"] == 55
    assert orchestrator.readiness(None, 50, None, 0)["missing"] == ["Resume match", "Interview practice"]


def test_kaggle_style_files_replace_demo_data(demo, tmp_path, monkeypatch):
    from app import datasets

    raw = tmp_path / "raw"
    raw.mkdir()
    description = "Build backend services with Python, SQL and Docker for customers."
    (raw / "jobs.csv").write_text(f'Job Title,Job Description\nBackend Developer,"{description}"\n', encoding="utf-8")
    (raw / "naukri.csv").write_text(
        f'jobtitle,company,joblocation_address,jobdescription,skills,postdate\nData Analyst,Acme,Pune,"{description}",SQL,2019-07-05 10:00:00 +0000\n',
        encoding="utf-8")
    (raw / "Resume.csv").write_text('ID,Resume_str,Category\n1,"Some resume text for testing only",HR\n', encoding="utf-8")
    monkeypatch.setattr(config, "RAW_DIR", raw)
    assert datasets.load_postings() == {"rows": 2, "files": ["jobs.csv", "naukri.csv"]}
    info = governance.dataset_info()
    assert not info["is_demo"] and info["confidence_cap"] == "Low"


def test_api_flow(demo):
    with TestClient(__import__("app.api", fromlist=["app"]).app) as client:
        assert client.get("/api/status").json()["dataset"]["is_demo"] is True
        assert client.get("/api/dashboard").status_code == 200
        created = client.post("/api/applications", json={"company": "A", "role": "B"}).json()
        assert client.patch(f"/api/applications/{created['id']}", json={"status": "APPLIED"}).json()["status"] == "APPLIED"
        assert client.post("/api/applications", json={"company": "", "role": ""}).status_code == 400
        review = client.post("/api/review", json={"resume_text": RESUME, "jd": JD, "company": "A", "role": "Backend Developer"}).json()
        assert review["status"] == "done"
        assert client.get("/api/postings/1").status_code == 200
        assert client.get("/api/nope").status_code == 404

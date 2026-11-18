"""Rebuild ../deliverables from a real run on a temporary database.

    python scripts/build_deliverables.py

Your own placement.db is not touched. Needs matplotlib only for the node graph.
"""
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

CODE = Path(__file__).resolve().parent.parent
OUT = CODE.parent / "deliverables"
sys.path.insert(0, str(CODE))
TMP = Path(tempfile.mkdtemp(prefix="prc_"))
os.environ["PRC_DB"] = str(TMP / "run.db")
os.environ["PRC_PROMPT_LOG"] = str(TMP / "prompts.jsonl")

from app import agents, config, datasets, db, governance, llm, memory, orchestrator, prompts, tools  # noqa: E402

ROLE_FILES = {"backend_student": "backend_developer", "data_student": "data_analyst", "frontend_student": "frontend_developer"}


def read(folder, name):
    return (folder / f"{name}.txt").read_text(encoding="utf-8")


def evaluate() -> dict:
    jds = {p.stem: p.read_text(encoding="utf-8") for p in sorted(config.DEMO_JDS.glob("*.txt"))}
    rows, correct = [], 0
    for resume_name, expected in ROLE_FILES.items():
        resume = read(config.DEMO_RESUMES, resume_name)
        scores = {jd: tools.resume_score(resume, text, jd.replace("_", " "))["total"] for jd, text in jds.items()}
        best = max(scores, key=scores.get)
        correct += best == expected
        rows.append({"resume": resume_name, "expected": expected, "best": best, "scores": scores})
    resume, jd = read(config.DEMO_RESUMES, "backend_student"), jds["backend_developer"]
    repeat = len({json.dumps(tools.resume_score(resume, jd, "Backend Developer"), sort_keys=True) for _ in range(20)}) == 1
    strong = tools.resume_score(resume, jd, "Backend Developer")["total"]
    weak = tools.resume_score(read(config.DEMO_RESUMES, "weak_resume"), jd, "Backend Developer")["total"]

    good = db.query("SELECT id FROM postings WHERE description LIKE '%Python%' LIMIT 1")[0]["id"]
    no_rust = db.query("SELECT id FROM postings WHERE description NOT LIKE '%Rust%' LIMIT 1")[0]["id"]
    claim = lambda skill, ids: {"text": "Forged claim", "skill": skill, "sample_size": 200, "support": 50, "citations": [{"posting_id": i} for i in ids]}
    attacks = [
        ("Market claim with no citation", not governance.verify_market_claims([claim("Python", [])])[0]),
        ("Citation to a posting that does not exist", not governance.verify_market_claims([claim("Python", [999999])])[0]),
        ("Citation that does not mention the skill", not governance.verify_market_claims([claim("Rust", [no_rust])])[0]),
        ("Thin evidence presented flatly", governance.LOW_LABEL in governance.verify_market_claims([{**claim("Python", [good]), "sample_size": 5, "support": 2}])[0][0]["text"]),
        ("Demo data claiming High confidence", governance.confidence_for(500, 200, "Medium") == "Medium"),
        ("Summary naming an unsupported company", bool(governance.check_narrative("Google is hiring.", "Python"))),
        ("Summary inventing a statistic", bool(governance.check_narrative("Demand rose 90%.", "Python 40"))),
        ("Bullet rewrite adding a skill", bool(governance.check_rewrite("Built an API", "Built a Docker API"))),
        ("Bullet rewrite adding a number", bool(governance.check_rewrite("Built an API", "Built an API for 500 users"))),
    ]
    return {"role_match": rows, "correct": correct, "total": len(rows), "repeatable": repeat, "strong": strong, "weak": weak,
            "attacks": [{"case": c, "blocked": bool(ok)} for c, ok in attacks]}


def run_tests() -> str:
    env = {k: v for k, v in os.environ.items() if k not in ("PRC_DB", "PRC_PROMPT_LOG")}
    result = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q", "--no-header"], cwd=CODE, env=env, capture_output=True, text=True)
    return result.stdout.strip().splitlines()[-1]


def demo_flow() -> dict:
    profile = memory.get_profile()
    app = next(a for a in tools.application_tracker("list")["applications"] if a["role"] == "Backend Developer")
    jd = app["job_description"]
    before = agents.review_resume(profile["resume_text"], jd, app["company"], app["role"], app["id"])
    target = next(r for r in before["recommendations"] if r["skill"] == "Docker")
    memory.add_feedback(target["text"], "rejected", "Docker", "I have not used Docker yet.", f"review {before['review_id']}")
    after = agents.review_resume(profile["resume_text"], jd, app["company"], app["role"], app["id"])
    questions = agents.interview_questions(jd, app["role"], app["id"])
    agents.evaluate_answer(questions["questions"][2], "We disagreed on an index versus a query rewrite. I tested both on real data, shared the "
                           "4 second and 600 ms results, and the team chose the index.", app["id"])
    return {"before": before, "after": after, "questions": questions, "report": orchestrator.weekly_report()}


def table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    return lines + ["| " + " | ".join(str(c).replace("|", "/") for c in row) + " |" for row in rows]


TRACE = [
    ("Tool: `resume_score(resume, jd)`", "`code/app/tools.py`", "Fixed rubric, repeatable score test"),
    ("Tool: `keyword_gap(resume, jd)`", "`code/app/tools.py`", "Missing-skill priority test"),
    ("Tool: `application_tracker(add/update)`", "`code/app/tools.py`", "Add, update, delete and validation test"),
    ("Skill: Resume-vs-JD review", "`code/skills/resume_jd_review/SKILL.md`", "Test compares file weights with code; file is sent in the rewrite prompt"),
    ("Memory: long-term profile", "`profile` table", "Used by every agent"),
    ("Memory: session state", "`session_state` table", "Stores today's application and last review"),
    ("Memory: accepted/rejected feedback retrieval", "`feedback` table, `code/app/memory.py`", "Rejected advice hidden on the next review"),
    ("MCP connector: postings and tracker", "`code/connector/mcp_server.py`", "Test calls it over real stdio"),
    ("Deep-research loop", "`code/app/research.py`", "Search widening and citation tests"),
    ("Swarm merged into weekly report", "`code/app/orchestrator.py`", "End-to-end report test"),
    ("Governance: cited claims, no invented facts", "`code/app/governance.py`", "Attack cases below"),
    ("Governance: low-confidence labelling", "`code/app/governance.py`", "Label test and attack case"),
    ("Guided intake, then rubric, then QA", "`code/app/agents.py`", "Intake test"),
]


def write_evidence(result, ev, tests):
    report = result["report"]
    lines = ["# Evidence Table", "", "Generated by `code/scripts/build_deliverables.py` from a real run.", "",
             "> The market figures use synthetic demo postings. They prove the pipeline works. They are not real labour-market findings.", "",
             "## 1. Requirement evidence", ""] + table(["Requirement", "Where", "How it is verified"], TRACE)
    lines += ["", "## 2. Measured results", ""] + table(["Check", "Result"], [
        ("Automated tests", tests),
        ("Resume ranks highest for its own role (demo set)", f"{ev['correct']} of {ev['total']}"),
        ("Same input gives the same score (20 runs)", "Yes" if ev["repeatable"] else "No"),
        ("Strong vs weak resume on the same JD", f"{ev['strong']} vs {ev['weak']}"),
        ("Governance attack cases blocked", f"{sum(a['blocked'] for a in ev['attacks'])} of {len(ev['attacks'])}"),
        ("Rejected advice removed on next review", "Yes" if "Docker" in [h["skill"] for h in result["after"]["hidden_by_memory"]] else "No"),
        ("Weekly report QA", "All passed" if report["qa_passed"] else "Failed"),
        ("Market connector transport", report["market"]["transport"]),
    ])
    lines += ["", "### Role-match scores", ""] + table(["Resume", "Expected JD", "Best JD", "All scores"],
        [(r["resume"], r["expected"], r["best"], ", ".join(f"{k}: {v}" for k, v in r["scores"].items())) for r in ev["role_match"]])
    lines += ["", "### Governance attack cases", ""] + table(["Attack", "Blocked"], [(a["case"], "Yes" if a["blocked"] else "No") for a in ev["attacks"]])
    lines += ["", "## 3. Claims in the sample weekly report", ""] + table(["ID", "Claim", "Evidence", "Source", "n", "Confidence"],
        [(e["id"], e["claim"], e["evidence"], e["source"], e["sample"], e["confidence"]) for e in report["evidence_table"]])
    (OUT / "evidence_table.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_memory_schema():
    conn = sqlite3.connect(config.db_path())
    purposes = {
        "profile": ("Long-term", "Skills, target roles, weak areas and resume"),
        "session_state": ("Session", "Today's application and last review"),
        "feedback": ("Retrieval store", "Advice accepted or rejected, with reasons"),
        "applications": ("Tracking store", "Every application and its current status"),
        "application_events": ("Tracking store", "Status history"),
        "postings": ("Evidence store", "Job postings cited by market claims"),
        "reviews": ("History", "Saved resume reviews"),
        "interview_attempts": ("History", "Mock answers and feedback"),
        "reports": ("History", "Saved weekly reports"),
    }
    lines = ["# Memory Schema", "", "Storage is one SQLite file, `code/placement.db`, defined in `code/app/db.py`.", "",
             "## Memory layers", ""] + table(["Table", "Layer", "Purpose"], [(k, *v) for k, v in purposes.items()])
    lines += ["", "## How feedback retrieval works", "",
              "1. Each new recommendation is compared with saved decisions.",
              "2. An exact skill match wins, and advice about a different skill never matches. Otherwise text cosine similarity must be at least 0.75.",
              "3. Rejected matches are hidden and shown with the student's reason.",
              "4. Accepted matches stay visible with a note.", "", "## Tables", ""]
    for table_name in purposes:
        lines += [f"### {table_name}", ""] + table(["Column", "Type", "Required", "Key"],
            [(c[1], c[2], "Yes" if c[3] else "No", "Yes" if c[5] else "") for c in conn.execute(f"PRAGMA table_info({table_name})")]) + [""]
    conn.close()
    (OUT / "memory_schema.md").write_text("\n".join(lines), encoding="utf-8")


def write_prompt_log():
    lines = ["# Prompt Log", "", "Part 1 lists the prompt templates. Part 2 is the log captured during the sample run.",
             "Emails and phone numbers are removed before a prompt is sent. Long text is shortened here.", "", "## Part 1. Templates", ""]
    for name in ("REWRITE_BULLETS", "INTERVIEW_QUESTIONS", "EVALUATE_ANSWER", "WEEKLY_SUMMARY"):
        lines += [f"### {name}", "", "```text", getattr(prompts, name).strip(), "```", ""]
    lines += ["## Part 2. Captured calls", ""]
    path = config.prompt_log_path()
    entries = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []
    if not entries:
        lines.append("No calls were captured.")
    for i, e in enumerate(entries, 1):
        lines += [f"### Call {i}: {e['task']}", "", f"- Time: {e['at']}", f"- Model: {e['model'] or 'none'}", f"- Status: {e['status']}", "",
                  "Prompt (end of text):", "", "```text", e["prompt"][-900:], "```", "", "Response:", "", "```text", (e.get("response") or "(no response)")[:1200], "```", ""]
    (OUT / "prompt_log.md").write_text("\n".join(lines), encoding="utf-8")


MERMAID = """flowchart TD
    S([Student]) --> I[Intake agent: clarify missing context]
    I -->|details missing| S
    I -->|ready| R[Resume-Reviewer]
    M[(Memory: profile, session, feedback)] --> R
    R --> T1[[resume_score]]
    R --> T2[[keyword_gap]]
    R --> Q1{QA: honesty note, no added facts}
    Q1 --> S
    S -->|accept or reject| M
    S --> W[Weekly report trigger]
    W --> A[Resume-Reviewer worker]
    W --> B[Interview-Coach worker]
    W --> C[Market-Analyst worker]
    M --> A
    M --> B
    C --> D1[Search] --> D2[Extract] --> D3[Compare] --> D4[Synthesize]
    D1 -->|too few postings: widen| D1
    D1 <--> X[MCP connector]
    X <--> P[(Job postings)]
    X <--> K[(Application tracker)]
    A --> G[Merge]
    B --> G
    D4 --> G
    G --> Q2{QA gate: citations, labels, facts}
    Q2 --> F([Weekly report and evidence table])
"""


def draw_graph():
    (OUT / "node_graph.mmd").write_text(MERMAID, encoding="utf-8")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

    fill = {"person": "#14352e", "agent": "#e2f0ec", "tool": "#f4f1e8", "store": "#e8edf5", "qa": "#fdf2d8"}
    nodes = {  # name: (x, y, half width, label, kind)
        "student": (50, 95, 9, "Student", "person"),
        "intake": (15, 82, 11, "Intake agent\nclarify missing context", "agent"),
        "review": (39, 82, 10, "Resume-Reviewer\nrubric + keyword gap", "agent"),
        "qa1": (85, 82, 13, "QA\nhonesty note, no added facts", "qa"),
        "memory": (10, 66, 9, "Memory: profile,\nsession, feedback", "store"),
        "trigger": (58, 68, 10, "Weekly report trigger", "person"),
        "rw": (26, 54, 10, "Resume-Reviewer\nworker", "agent"),
        "iw": (52, 54, 10, "Interview-Coach\nworker", "agent"),
        "mw": (80, 54, 10, "Market-Analyst\nworker", "agent"),
        "search": (92, 40, 6.5, "1. Search", "tool"),
        "extract": (78, 40, 6, "2. Extract", "tool"),
        "compare": (64, 40, 6, "3. Compare", "tool"),
        "synth": (49, 40, 7, "4. Synthesize", "tool"),
        "merge": (26, 40, 8, "Merge", "agent"),
        "mcp": (88, 26, 9, "MCP connector", "tool"),
        "post": (76, 12, 9, "Job postings", "store"),
        "track": (92, 12, 6.5, "Application\ntracker", "store"),
        "qa2": (26, 26, 12, "QA gate\ncitations, labels, facts", "qa"),
        "final": (26, 12, 12, "Weekly report +\nevidence table", "person"),
    }
    edges = [("student", "intake"), ("intake", "review"), ("review", "qa1"), ("qa1", "student"), ("memory", "review"), ("student", "trigger"),
             ("trigger", "rw"), ("trigger", "iw"), ("trigger", "mw"), ("memory", "rw"), ("mw", "search"), ("search", "extract"), ("extract", "compare"),
             ("compare", "synth"), ("search", "mcp"), ("mcp", "post"), ("mcp", "track"), ("rw", "merge"), ("iw", "merge"), ("synth", "merge"),
             ("merge", "qa2"), ("qa2", "final")]
    fig, ax = plt.subplots(figsize=(13, 9.5))
    ax.set(xlim=(0, 100), ylim=(3, 100))
    ax.axis("off")
    h, boxes = 3.6, {}
    for name, (x, y, w, text, kind) in nodes.items():
        boxes[name] = FancyBboxPatch((x - w, y - h), 2 * w, 2 * h, boxstyle="round,pad=0,rounding_size=1", fc=fill[kind], ec="#66736d", lw=.9, zorder=2)
        ax.add_patch(boxes[name])
        ax.text(x, y, text, ha="center", va="center", fontsize=9.5, color="white" if kind == "person" else "#1d2522", zorder=3)
    for a, b in edges:
        ax.add_patch(FancyArrowPatch(nodes[a][:2], nodes[b][:2], patchA=boxes[a], patchB=boxes[b], arrowstyle="-|>", mutation_scale=13,
                                     color="#55625c", lw=1.2, shrinkA=1, shrinkB=2, zorder=1))
    ax.text(70, 33, "Too few postings? Search widens:\nexact role, role words, all postings", ha="center", va="center", fontsize=9, color="#5d6a64")
    fig.savefig(OUT / "node_graph.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    OUT.mkdir(exist_ok=True)
    datasets.setup(reset=True)
    print("AI:", "on" if llm.available() else "off")
    ev = evaluate()
    result = demo_flow()
    tests = run_tests()
    write_evidence(result, ev, tests)
    write_memory_schema()
    write_prompt_log()
    draw_graph()
    (OUT / "weekly_report_sample.md").write_text(orchestrator.to_markdown(result["report"]), encoding="utf-8")
    shutil.copy(config.SKILL_FILE, OUT / "skill_file_resume_jd_review.md")
    summary = {"evaluation": ev, "tests": tests, "report": result["report"], "review": result["after"], "questions": result["questions"]}
    (TMP / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
    target = os.getenv("PRC_SUMMARY_OUT")
    if target:
        shutil.copy(TMP / "summary.json", target)
    print("Tests:", tests)
    print("Role match:", ev["correct"], "of", ev["total"], "| attacks blocked:", sum(a["blocked"] for a in ev["attacks"]), "of", len(ev["attacks"]))
    print("Report QA:", result["report"]["qa_passed"], "| transport:", result["report"]["market"]["transport"], "| summary:", result["report"]["summary_source"])


if __name__ == "__main__":
    main()

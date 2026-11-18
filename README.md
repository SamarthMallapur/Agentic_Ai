# Placement Readiness Companion

An agentic assistant that stays with one student through a placement season. It reviews resumes, tracks applications, coaches for interviews and produces a cited weekly report.

**GitHub repository:** https://github.com/SamarthMallapur/Agentic_Ai

## Standout features

- **Agent Mission Control:** watch the real agents and research steps run live while the weekly report is built.
- **What-If Simulator:** choose honest resume improvements and see the estimated rubric score change instantly.
- **Career Compass:** get a cited, ranked skill roadmap and best-fit jobs you can track in one click.
- **Timed Voice Interview:** answer against a timer by typing or speaking, then review pace, filler words and content.
- **Readiness Trend:** follow your calculated readiness across weekly reports.

## Run it

Python 3.10 or newer is the only requirement.

```bash
cd code
python -m pip install -r requirements.txt
python run.py
```

The app opens at http://127.0.0.1:8000 with a sample student. Full instructions are in [code/README.md](code/README.md).

## Submission contents

| Requirement | Location |
|---|---|
| Detailed Project Report | [report/Detailed_Project_Report.docx](report/Detailed_Project_Report.docx) |
| Executable code, dependencies and run instructions | [code/](code/) |
| GitHub repository link | Top of this file and in the report |
| Working demo | [deliverables/demo_walkthrough.md](deliverables/demo_walkthrough.md), [deliverables/screenshots/](deliverables/screenshots/) |
| AI agents used, and how | [deliverables/agents.md](deliverables/agents.md) |
| Evidence table | [deliverables/evidence_table.md](deliverables/evidence_table.md) |
| Node graph | [deliverables/node_graph.png](deliverables/node_graph.png), [Mermaid source](deliverables/node_graph.mmd) |
| Skill file | [deliverables/skill_file_resume_jd_review.md](deliverables/skill_file_resume_jd_review.md) |
| Memory schema | [deliverables/memory_schema.md](deliverables/memory_schema.md) |
| Prompt log | [deliverables/prompt_log.md](deliverables/prompt_log.md) |
| Weekly report sample | [deliverables/weekly_report_sample.md](deliverables/weekly_report_sample.md) |
| Limitations note | [deliverables/limitations.md](deliverables/limitations.md) |

## Folder structure

```text
placement-readiness-companion/
├── README.md                     Start here
├── report/
│   └── Detailed_Project_Report.docx
├── code/                         Everything needed to run the project
│   ├── README.md                 Run instructions
│   ├── requirements.txt
│   ├── .env.example
│   ├── run.py                    One-command start
│   ├── app/                      Agents, tools, memory, research, QA, API
│   ├── connector/                MCP server
│   ├── skills/                   Resume-vs-JD skill
│   ├── data/                     Demo data, and a folder for Kaggle CSV files
│   ├── frontend/                 React source
│   ├── web/                      Built web app
│   ├── scripts/                  Demo data and deliverable builders
│   └── tests/
└── deliverables/                 Evidence, graph, schema, logs and samples
```

## Before submitting

1. Fill in your name, ID and guide on the first page of the report.
2. Push the final code to GitHub, then open the repository link in a private browser window to confirm it shows this folder structure.
3. Never submit `code/.env`, because it contains your API key. It is excluded from Git.

## Important data note

The included job postings are synthetic demo data, and the app labels them so. To use real data, follow [code/data/raw/README.md](code/data/raw/README.md).

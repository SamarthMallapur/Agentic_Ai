# AI Agents Used

The project has six cooperating agents. They are plain Python modules, so each step can be inspected and tested. No agent framework is used.

Rules make every decision that must be repeatable, such as scores, citations and confidence labels. Gemini is used only for wording tasks. The default model is `gemini-3.1-flash-lite`, with `gemini-3.8-flash` as the fallback. Without a key, the app uses rule-based fallbacks.

| Agent | Job | How it works | Uses Gemini? | Code |
|---|---|---|---|---|
| Intake | Finds missing context | Checks the resume, JD, role and company, then asks before reviewing | No | `app/agents.py`, `intake` |
| Resume-Reviewer | Scores a resume against a JD | Calls `resume_score` and `keyword_gap`, then applies feedback memory | Only for bullet rewrites | `app/agents.py`, `review_resume` |
| Interview-Coach | Creates questions and scores answers | Uses the JD, skill gaps and profile | Yes, with a question bank and rule-based fallback | `app/agents.py`, `interview_questions`, `evaluate_answer` |
| Market-Analyst | Researches skill demand | Runs search, extract, compare and synthesize through the MCP connector | No | `app/research.py` |
| Report Editor | Merges the weekly report | Builds the action plan by rules, then writes a summary from verified facts | Only for the summary | `app/orchestrator.py` |
| QA / Governance | Checks output before the student sees it | Verifies citations, confidence labels, added skills, numbers and company names | No | `app/governance.py` |

## How they work together

**Resume review:** Intake → Resume-Reviewer → QA → student. The student's accept or reject decision goes into memory and affects later reviews.

**Weekly report:** Resume-Reviewer, Interview-Coach and Market-Analyst run in parallel. Report Editor merges their results, and QA checks the report before it is saved and shown.

If Gemini text fails a QA check, it is discarded and the rule-based version is used.

Mission Control on the Weekly Report page shows these steps from live server events. The What-If Simulator, Career Compass and delivery analysis are rule-based decision tools in `app/insights.py`, so they are not counted as separate AI agents.

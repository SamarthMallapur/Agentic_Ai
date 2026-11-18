# Run the Placement Readiness Companion

You only need **Python 3.10 or newer**. Node.js is not needed, because the web app is already built.

## 1. Open a terminal in this `code` folder

```bash
cd code
```

## 2. Install the dependencies

```bash
python -m pip install -r requirements.txt
```

## 3. Optional: turn on AI wording

The app works without a key. A free Gemini key adds resume bullet rewrites, tailored interview questions,
AI answer feedback and a written report summary.

Windows:

```bash
copy .env.example .env
```

macOS or Linux:

```bash
cp .env.example .env
```

Open `.env` and replace `your_gemini_api_key_here` with your key from https://aistudio.google.com/apikey.

## 4. Start the app

```bash
python run.py
```

Your browser opens at http://127.0.0.1:8000. Press `Ctrl+C` in the terminal to stop.

## Use it in 5 steps

The app starts with a sample student, so every page has data straight away.

| Step | Page | What to do |
|---|---|---|
| 1 | My Profile | Replace the sample with your resume, skills and target roles, then save |
| 2 | Applications | Add a company, role and job description |
| 3 | Resume Review | Pick the application, press **Review my resume**, then accept or reject advice |
| 4 | Interview Coach | Pick the application, create questions, write answers, get feedback |
| 5 | Weekly Report | Press **Generate new report** and open the sources behind each claim |

## Useful commands

| Task | Command |
|---|---|
| Start again with clean demo data (deletes saved data) | `python run.py --reset` |
| Start without opening a browser | `python run.py --no-browser` |
| Run the tests | `python -m pytest tests -q` |
| Start the MCP connector alone | `python connector/mcp_server.py` |
| Rebuild the `deliverables` folder (also needs `matplotlib`) | `python scripts/build_deliverables.py` |

## Use real job data

The included postings are synthetic. To use Kaggle data, follow [data/raw/README.md](data/raw/README.md).

## Change the web app (optional, needs Node.js 20+)

```bash
cd frontend
npm install
npm run build
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `Missing packages` | Run step 2 again |
| `python` is not recognised | Try `py` in place of `python` |
| AI wording shows **Off** | Check `code/.env`, then restart the app |
| Port 8000 is busy | The app picks the next free port and prints it |
| A scanned PDF gives no text | Paste the resume text instead |

## Folder guide

| Path | Contents |
|---|---|
| `run.py` | Starts everything |
| `app/tools.py` | `resume_score`, `keyword_gap`, `application_tracker` |
| `app/agents.py` | Intake, Resume-Reviewer and Interview-Coach |
| `app/research.py` | Search, extract, compare, synthesize loop |
| `app/orchestrator.py` | Agent swarm and weekly report |
| `app/governance.py` | QA rules |
| `app/memory.py`, `app/db.py` | Memory and database schema |
| `connector/mcp_server.py` | MCP connector |
| `skills/resume_jd_review/SKILL.md` | Review skill |
| `data/` | Demo postings, resumes and job descriptions |
| `frontend/`, `web/` | React source and its built version |
| `tests/` | Automated tests |

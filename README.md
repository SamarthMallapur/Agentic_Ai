# Placement Readiness Companion

"One AI companion that stays with a student throughout the entire placement season."

## Project Overview
This is a persistent, multi-agent AI companion designed to help students prepare for their placement season. It tracks long-term career profiles, analyzes resumes, manages applications, conducts mock interviews, and researches the job market.

## Architecture
- **UI:** Streamlit
- **Orchestrator:** Google ADK Agents
- **Models:** Gemini 3.1 Flash Lite via `google-genai`
- **Memory/DB:** SQLite
- **MCP Server:** Exposes memory and market data to agents cleanly.

## Setup Instructions

1. **Clone the repo** and navigate to the directory.
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set Environment Variables**:
   ```bash
   # .env
   GEMINI_API_KEY=your_api_key
   ```
4. **Initialize the Database & Seed Data**:
   ```bash
   python database/models.py
   python data/seed_data/seed.py
   python scripts/ingest_jobs.py
   ```
5. **Run the Dashboard**:
   ```bash
   streamlit run app.py
   ```

## Workflow
- **Dashboard**: View overall readiness score.
- **My Profile**: View and edit your long-term preferences and skills.
- **Resume Analyzer**: Paste a JD and get a 100-point rubric score and actionable gaps.
- **Applications Tracker**: Add and manage job applications.
- **Interview Coach**: Select an application and get 5 tailored mock questions based on your resume and identified weak spots.
- **Market Trends**: See aggregated statistics on local job data.
- **Weekly Report**: Generate a full readiness report with Evidence Tables and Recommended Actions.

## Known Limitations
Please see `docs/limitations.md`.

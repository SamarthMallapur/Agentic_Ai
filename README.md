# Placement Readiness Companion

> "One AI companion that stays with a student throughout the entire placement season."

## Project Overview
**Placement Readiness Companion** is a persistent, multi-agent AI application designed to guide and empower students through their placement season. It tracks long-term career profiles, analyzes resumes against job descriptions, manages applications, conducts targeted mock interviews, and surfaces market trends.

---

## Architecture
- **Frontend:** React + Vite (Modern SPA with responsive dashboard, analytics, and interview coaching UI)
- **Backend API:** FastAPI (Async Python REST API)
- **Orchestration:** Google ADK Agents
- **Models:** Gemini 3.1 Flash Lite via `google-genai`
- **Memory & Storage:** SQLite (`database/models.py`)
- **MCP Server:** Exposes persistent memory and job market data to agents cleanly

---

## Quick Start (Single Command)

### 1. Prerequisites
- **Python 3.8+**
- **Node.js** (v18+) and **npm**

### 2. Configure Environment
Copy `.env.example` to `.env` and set your Gemini API Key:
```bash
cp .env.example .env
```
*(Add your Gemini API key inside `.env`: `GEMINI_API_KEY=your_gemini_api_key_here`)*

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Everything
Execute the all-in-one startup script:
```bash
python start.py
```
*(or `python run.py`)*

This script automatically:
- Checks and initializes the database and seed data if missing (`database/models.py`, `data/seed_data/seed.py`, `scripts/ingest_jobs.py`).
- Installs frontend packages (`npm install`) if `node_modules` is not yet installed.
- Starts the **FastAPI Backend** on `http://localhost:8000`.
- Starts the **React Frontend** on `http://localhost:5173`.
- Automatically opens `http://localhost:5173` in your default browser.
- Cleans up both background processes when you press `Ctrl+C`.

---

## Manual Setup (Step-by-Step)

If you prefer running backend and frontend in separate terminals:

### Terminal 1: Backend
```bash
# 1. Initialize Database & Ingest Seed Data (first time only)
python database/models.py
python data/seed_data/seed.py
python scripts/ingest_jobs.py

# 2. Start FastAPI Server
python api.py
```
- API is live on: `http://localhost:8000`
- Interactive Swagger Docs: `http://localhost:8000/docs`

### Terminal 2: Frontend
```bash
cd frontend
npm install
npm run dev
```
- Web Application is live on: `http://localhost:5173`

---

## Features & Workflow
- **Dashboard**: High-level overview of readiness score, active applications, interviews, and offers.
- **My Profile**: View and edit long-term career preferences, technical skills, and target roles.
- **Resume Analyzer**: Upload a PDF or paste resume text against a Job Description to get a 100-point rubric breakdown and actionable skill gaps.
- **Applications Tracker**: Add, track, and update status on ongoing applications.
- **Interview Coach**: Tailored mock interview questions generated based on student profile and identified weak spots.
- **Market Trends**: Aggregated statistics and trending skills from local job market data.
- **Weekly Report**: Full multi-agent readiness report with Evidence Tables and recommended next steps.

---

## Known Limitations
Please refer to [docs/limitations.md](docs/limitations.md).

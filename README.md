# Placement Readiness Companion

> "One AI companion that stays with a student throughout the entire placement season."

## Project Overview
**Placement Readiness Companion** is a persistent, multi-agent AI application designed to guide and empower students through their placement season. It tracks long-term career profiles, analyzes resumes against job descriptions, manages applications, conducts targeted mock interviews, and surfaces market trends.

---

## Architecture
- **Frontend:** React + Vite (Modern SPA with Tailwind/custom responsive styling and routing)
- **Backend API:** FastAPI (Async Python REST API)
- **Orchestration:** Google ADK Agents
- **Models:** Gemini 3.1 Flash Lite via `google-genai`
- **Memory & Storage:** SQLite (`database/models.py`)
- **MCP Server:** Exposes persistent memory and job market data to agents cleanly

---

## Getting Started

### 1. Prerequisites
- **Python 3.8+**
- **Node.js** (v18+) and **npm**

### 2. Backend Setup
1. **Navigate to the project root**:
   ```bash
   cd placement-readiness-companion
   ```
2. **Create and activate a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure Environment Variables**:
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Add your Gemini API Key in `.env`:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
5. **Initialize Database & Ingest Seed Data**:
   ```bash
   python database/models.py
   python data/seed_data/seed.py
   python scripts/ingest_jobs.py
   ```
6. **Start the FastAPI Backend Server**:
   ```bash
   python api.py
   ```
   *The backend will run on `http://localhost:8000` (API docs at `http://localhost:8000/docs`).*

### 3. Frontend Setup (React)
1. In a new terminal, navigate to the `frontend` folder:
   ```bash
   cd frontend
   ```
2. **Install dependencies**:
   ```bash
   npm install
   ```
3. **Start the Vite development server**:
   ```bash
   npm run dev
   ```
   *The React web app will run locally (typically at `http://localhost:5173`).*

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

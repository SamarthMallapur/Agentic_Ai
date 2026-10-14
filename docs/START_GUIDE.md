# How to Start and Run the Program

The Placement Readiness Companion consists of a FastAPI backend and a Vite/React frontend.

---

## ⚡ Option 1: Quick Start (Single Command)

You can launch both the backend and frontend simultaneously using the provided runner script:

```bash
python start.py
```
*(or `python run.py`)*

### What `start.py` does automatically:
1. Copies `.env.example` to `.env` if not present.
2. Checks if `placement.db` exists; if not, automatically executes database creation and seed ingestion.
3. Checks if `frontend/node_modules` exists; if not, runs `npm install`.
4. Starts the FastAPI backend on `http://localhost:8000`.
5. Starts the Vite React frontend on `http://localhost:5173`.
6. Launches your default web browser to `http://localhost:5173`.
7. Gracefully stops all child processes when you press `Ctrl+C`.

> **Note:** If you do not want the browser to pop open automatically, use:
> ```bash
> python start.py --no-browser
> ```

---

## 🛠 Option 2: Manual Start (Separate Terminals)

### 1. Prerequisites
- **Python 3.8+**
- **Node.js** (v18+ recommended) and **npm**

### 2. Environment Setup
```bash
cp .env.example .env
```
Open `.env` and set your `GEMINI_API_KEY`:
```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 3. Backend Setup & Database Initialization
```bash
# Optional virtualenv
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Dependencies
pip install -r requirements.txt

# Seed Database
python database/models.py
python data/seed_data/seed.py
python scripts/ingest_jobs.py
```

### 4. Running the Servers Concurrently

**Terminal 1 (Backend - FastAPI):**
```bash
python api.py
```
*(API live on `http://localhost:8000`, docs at `http://localhost:8000/docs`)*

**Terminal 2 (Frontend - React):**
```bash
cd frontend
npm install
npm run dev
```
*(Frontend live on `http://localhost:5173`)*

---

## Troubleshooting
- **Port Conflicts**: If port `8000` or `5173` is in use, make sure to terminate any existing processes using those ports.
- **Database Errors**: If you encounter SQLite errors, ensure that you ran the initialization scripts in the exact order listed in Step 3.
- **API Key Errors**: Ensure your `.env` file is named exactly `.env` and placed in the project root directory.

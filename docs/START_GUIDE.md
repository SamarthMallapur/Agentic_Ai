# How to Start and Run the Program

The Placement Readiness Companion consists of a backend (with both Streamlit and FastAPI options) and a Vite/React frontend.

Follow the steps below to set up and run the entire application.

## 1. Prerequisites
Ensure you have the following installed:
- **Python 3.8+**
- **Node.js** (v18+ recommended) and **npm**

## 2. Environment Setup

1. **Clone the repository** and navigate to the project root directory.
2. **Set up the Environment Variables**:
   Copy the example environment file:
   ```bash
   cp .env.example .env
   ```
   Open the `.env` file and add your Gemini API Key:
   ```env
   GEMINI_API_KEY=your_actual_api_key_here
   ```

## 3. Backend Setup & Database Initialization

1. **Install Python Dependencies**:
   It is recommended to use a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Initialize the Database and Seed Data**:
   Run the following scripts from the project root to create the SQLite database and populate it with initial data:
   ```bash
   python database/models.py
   python data/seed_data/seed.py
   python scripts/ingest_jobs.py
   ```

## 4. Running the Application

You can interact with the companion through either the **Streamlit Dashboard** or the **React Web App**.

### Option A: Run the Streamlit Dashboard
The Streamlit app is a standalone dashboard that provides a full interface without needing the React frontend.
```bash
streamlit run app.py
```
This will automatically open the Streamlit dashboard in your browser (usually at `http://localhost:8501`).

### Option B: Run the FastAPI Backend and React Frontend
If you prefer to use the React-based frontend, you will need to run the FastAPI server and the Vite dev server concurrently.

**Terminal 1 (Backend - FastAPI):**
Start the FastAPI server from the project root:
```bash
python api.py
```
*(The backend will run on `http://localhost:8000`)*

**Terminal 2 (Frontend - React):**
Navigate to the `frontend` directory, install dependencies, and start the development server:
```bash
cd frontend
npm install
npm run dev
```
*(The Vite frontend will run on the URL provided in the terminal output, typically `http://localhost:5173`)*

---

## Troubleshooting
- **Port Conflicts**: If port `8000`, `8501`, or `5173` are in use, make sure to kill any existing processes using those ports.
- **Database Errors**: If you encounter SQLite errors, ensure that you ran the initialization scripts in the exact order listed in Step 3.
- **API Key Errors**: Ensure your `.env` file is named exactly `.env` (not `.env.txt`) and placed in the project root.

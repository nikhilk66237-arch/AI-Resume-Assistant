# AI Resume Analyzer

An intelligent, production-ready career alignment platform and ATS optimizer. The application analyzes a candidate's resume against target career roles and employer Job Descriptions (JDs) using a secure backend AI integration (Google Gemini) and a transparent mathematical scoring engine.

---

## 🌟 Overview

The **AI Resume Analyzer** evaluates candidate qualifications against industry competency benchmarks and company-specific job postings. It parses resumes in PDF, Word (DOCX), or plain text format, detects competencies and sections, compares gaps, conducts an in-depth Applicant Tracking System (ATS) audit, and provides prioritized, actionable recommendations to maximize interview callbacks.

---

## ✨ Features

- **Multi-Format Resume Parsing**: Securely validates and parses PDF (`.pdf`), Word (`.docx`), and text (`.txt`) documents up to 5 MB with magic-byte verification (`%PDF`, `PK`) and table text extraction.
- **Target Role Analysis**: Calibrated benchmarks across standard industry tracks (*Python Developer*, *Full Stack Developer*, *Data Analyst*, *Data Scientist*, *AI/ML Engineer*, *Cybersecurity Analyst*, *Cloud Engineer*, *DevOps Engineer*, *Software Engineer*, or any custom role).
- **Job Description (JD) Analysis**: When a job description is supplied, employer-specific requirements are dynamically parsed and prioritized over generic defaults.
- **Resume ↔ Target Role Match Percentage**: Deterministic, weighted mathematical scoring across 10 distinct categories.
- **3-Way Skills Gap Analysis**:
  - **✓ Matching Skills**: Competencies present in both the resume and target role.
  - **✕ Missing Skills**: Core competencies required/recommended for the role but absent from the resume.
  - **＋ Additional Skills**: Bonus competencies found on the resume not explicitly required.
- **Target Role Requirements Matrix**: Clean breakdown into *Required Skills*, *Recommended Skills*, *Optional Skills*, and domain toolchains.
- **ATS Readiness Audit**: Comprehensive score, section checklist, format verification, and roadblock warnings.
- **Resume Quality Assessment**: Highlights verified resume strengths, detected weaknesses, missing elements, and formatting gaps.
- **Personalized Improvement Suggestions**: Prioritized into **HIGH**, **MEDIUM**, and **LOW PRIORITY** action items with before-and-after bullet point rewrites.
- **Role Compatibility Analysis**: Benchmarks candidate compatibility index across alternative tech career pathways with realistic guidance.
- **Secure Backend Gemini Integration**: Server-side only Google Gemini API calls with zero secret leakage to the client.
- **Responsive Dashboard**: Modern Streamlit user interface with high visual clarity, progress bars, and badge pills.
- **Downloadable Analysis Report**: Exports a comprehensive analytical summary report in Markdown (`.md`) format.

---

## 🛠️ Tech Stack

- **Core Language**: Python 3.10+
- **Backend API Framework**: [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) (Asynchronous REST API)
- **Frontend Dashboard**: [Streamlit](https://streamlit.io/) with responsive custom HTML/CSS components
- **AI / LLM Engine**: [Google Gemini API](https://ai.google.dev/) (`google-generativeai` SDK)
- **Document Parsers**:
  - [PyPDF](https://pypdf.readthedocs.io/) (PDF extraction with stream verification)
  - [python-docx](https://python-docx.readthedocs.io/) (Word document paragraph & table extraction)
- **Data Validation & Schemas**: [Pydantic v2](https://docs.pydantic.dev/)
- **HTTP Client**: [Requests](https://requests.readthedocs.io/)
- **Configuration & Security**: [python-dotenv](https://github.com/theskumar/python-dotenv)

---

## 🏗️ Architecture

```
User
  │
  ▼
Streamlit Frontend (Port 8501)
  │
  │  POST /api/analyze-resume (JSON payload, zero secrets)
  ▼
FastAPI Backend (Port 8000)
  │
  ├──► Resume Parser (Magic-byte verification, PDF / DOCX extraction)
  │
  ├──► Analysis Engine (Deterministic 10-metric mathematical scoring)
  │
  ├──► Google Gemini API (Server-side only via GEMINI_API_KEY from .env)
  │
  ▼
Structured Analysis (Pydantic Response Model)
  │
  ▼
Results Dashboard (Streamlit UI with Hero Card, Metrics, Badges & Report)
```

---

## ⚙️ Installation & Setup (Windows)

Follow these exact Windows PowerShell / Command Prompt commands to set up the project locally:

### 1. Clone or Open the Repository
```powershell
cd "c:\path\to\Ai Resume Assistant"
```

### 2. Create and Activate Virtual Environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```
*(If using Command Prompt `cmd.exe`, run: `.\.venv\Scripts\activate.bat`)*

### 3. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the `.env.example` template to `.env`:
```powershell
copy .env.example .env
```
Open `.env` in any text editor and supply your Gemini API key:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
MAX_UPLOAD_MB=5
GEMINI_MODEL=gemini-1.5-flash
```

> **Note**: If `GEMINI_API_KEY` is not provided or offline, the application automatically uses its built-in deterministic rule scoring engine without errors.

---

## 🚀 Running the Application

The application consists of two decoupled services: the FastAPI backend and the Streamlit frontend.

### Terminal 1: Start the FastAPI Backend
```powershell
.\.venv\Scripts\Activate.ps1
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
*API interactive documentation will be available at: `http://127.0.0.1:8000/docs`*

### Terminal 2: Start the Streamlit Frontend
```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app.py
```
*The web dashboard will automatically open in your default browser at: `http://localhost:8501`*

---

## 🔒 Security & Privacy

- **Server-Side Credentials**: `GEMINI_API_KEY` is accessed exclusively by `backend/gemini_service.py` through backend environment variables.
- **Zero Client-Side Leakage**: The Streamlit frontend contains no API keys, no `.env` reading code, and no Gemini SDK imports.
- **Git Protection**: Sensitive files (`.env`, `.env.*`, keys) and uploaded resume files (`*.pdf`, `*.docx`) are strictly ignored in `.gitignore`.
- **Payload Verification**: Uploaded files undergo size enforcement (5 MB limit) and magic-byte header validation before processing.

---

## 📖 Step-by-Step Usage

1. **Open Application**: Navigate to `http://localhost:8501` in your browser.
2. **Upload Resume**: In **Step 1**, drag and drop your resume file (`.pdf`, `.docx`, `.txt`) or switch to the text tab to paste plain text.
3. **Select / Enter Target Role**: In **Step 2**, pick a target career track from the dropdown (e.g. *Python Developer*, *Data Analyst*) or enter a custom role.
4. **Add Optional Job Description**: In **Step 3**, paste the employer's specific job posting text to activate direct JD alignment scoring.
5. **Click Analyze**: In **Step 4**, click **🚀 Analyze Resume** to run the pipeline.
6. **Review Results**:
   - Inspect the **Overall Resume ↔ Target Role Match** score card.
   - Review the **10-Metric Breakdown** grid.
   - Examine the **Employer JD Direct Comparison** (when JD is supplied).
   - Explore **Matching**, **Missing**, and **Additional Skills** badges.
   - Read prioritized **Improvement Suggestions** (High / Medium / Low).
   - Review **ATS Readiness Audit** strengths and roadblock warnings.
   - Download the full analytical report via the **📥 Download Full Analysis Report (.md)** button.

---

## 📂 Project Structure

```
Ai Resume Assistant/
├── .env.example               # Safe environment variable configuration template
├── .gitignore                  # Git ignore rules (secrets, venv, resumes, temp files)
├── README.md                   # Project documentation and setup guide
├── requirements.txt            # Production dependencies
├── app.py                      # User-facing Streamlit dashboard frontend
├── analyzer.py                 # Backward-compatibility API facade
└── backend/                    # Decoupled FastAPI backend package
    ├── __init__.py             # Package initializer
    ├── main.py                 # FastAPI application and REST endpoints
    ├── models.py               # Pydantic data schemas and response contracts
    ├── parser.py               # Secure PDF, DOCX, and TXT parser with magic bytes
    ├── role_taxonomy.py        # Industry role competencies and skill aliases
    ├── scorer.py               # Transparent 10-metric mathematical scoring engine
    └── gemini_service.py       # Server-side Gemini AI integration & fallback
```

---

## 🔮 Future Improvements

- **User Authentication & Profiles**: Secure user login with saved resume history.
- **Resume Versioning & Comparison**: Side-by-side diff tracking between resume revisions over time.
- **Job Application Tracker**: Kanban board to organize applied roles, interview stages, and customized resume versions.
- **Cloud Database Integration**: PostgreSQL/Supabase persistence for candidate analytics and history.
- **Additional Document Formats**: Rich text format (`.rtf`) and LaTeX (`.tex`) parsing.
- **Direct PDF Export**: One-click generation of styled PDF report downloads alongside Markdown.
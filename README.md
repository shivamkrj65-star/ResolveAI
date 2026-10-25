# RESOLVEAI — Three Role-Based Portals Architecture

> **Hackathon**: Reforged '26 (BPIT, MLH, Unstop)  
> **Team**: HackShift_404  
> **Members**: Anshul Gupta (Team Leader) • Aditya Gupta • Shivam Jhingan  
> *Primary Track*: n8n Workflow Automation (Sponsored Track)

---

## 1. Project Overview

Free-form maintenance reports filed by campus students frequently generate duplicate tickets, ambiguous categorization, and inconsistent triage, severely slowing down repair velocity and wasting facility resources.

**ResolveAI** transforms unstructured text complaints into organized, schema-validated, auditable work orders. By integrating **Google Gemma** for structured entity extraction, **OpenCV** for computer vision validation, **Cloudinary** for secure evidence delivery, a **Hybrid Duplicate Detection Engine** combining vector semantics with physical building proximity and temporal decay, and **n8n Workflow Automation** for intelligent dispatch, ResolveAI ensures repairs are routed quickly, duplicates are flagged with empirical mathematical evidence, and administrative teams retain full audit oversight.

---

## 2. Three Role-Based Portals

ResolveAI features a role-separated portal architecture:

### 👤 1. USER PORTAL — Public Access (No Login)
- **Campus Problem Submission**: Free-form text issue submission with automatic category and location extraction.
- **OpenCV Image Processing**: Real-time image validation, decompression protection, blur detection, brightness/contrast metrics, and 64-bit perceptual dHash computation.
- **Cloudinary Image Storage**: Validated photos are uploaded securely to Cloudinary with optimized CDN delivery and thumbnail generation.
- **Public Complaint Tracking**: Students and reporters can track their complaint status, assigned department, and audit history live using their Ticket ID (e.g. `RES-2026-101`) or Case ID without logging in.

### 🛡️ 2. ADMIN PORTAL — Protected (Role: `admin`)
- **Admin Maintenance Triage**: Centralized queue with real-time updates for newly submitted complaints.
- **Search & Advanced Filtering**: Filter by category, authoritative priority level, status, building location, and search text.
- **Human-in-the-Loop Duplicate Review**: Inspect multimodal candidate duplicates (semantic similarity + physical proximity + temporal proximity + visual similarity) and confirm merges or approve separate dispatch.
- **Priority Calibration & Auditing**: Inspect calculated priority scores, safety-floor rules, and complete event history timelines.
- **Demo Credentials**:
  - **User ID**: `admin_resolve`
  - **Password**: `MapleFox47`
  - *(Configurable via `ADMIN_USERNAME` and `ADMIN_PASSWORD` in `backend/.env`)*

### 🧪 3. TESTING PORTAL — Protected (Role: `tester`)
- **n8n Automation Engine**: Interactive workflow graphs, webhook payloads, idempotency keys, and live execution run history.
- **Empirical Benchmarks & Ablation Study**: Evaluated on held-out fictional campus datasets showing 92.7% Macro-F1 across 8 categories, 94.1% duplicate recall, and ablation comparisons.
- **Notion Documentation & Test Sync**: Integrates the official Notion API to synchronize project architecture, benchmark results, and workflow execution snapshots to a Notion workspace.
- **Demo State Reset**: 1-click state reset for evaluators to rerun benchmark scenarios from a clean baseline.
- **Demo Credentials**:
  - **User ID**: `tester_resolve`
  - **Password**: `OrbitPanda82`
  - *(Configurable via `TESTER_USERNAME` and `TESTER_PASSWORD` in `backend/.env`)*

---

## 3. Technology Stack & Integrations

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide Icons
- **Backend**: FastAPI, Pydantic v2, Scikit-Learn, NumPy, Uvicorn, Python-dotenv
- **Computer Vision**: OpenCV (`opencv-python-headless`) for image decoding, blur variance, perceptual dHash, and visual feature extraction
- **Cloud Storage**: Cloudinary Python SDK for secure evidence hosting with automatic rollback
- **Documentation Sync**: Official Notion Python Client (`notion-client`)
- **Automation / Orchestration**: n8n Webhook Architecture with Idempotency Key protection
- **NLP / ML**: Google Gemma / Gemini API (with deterministic offline campus extraction engine fallback)
- **Testing**: Pytest unit & integration test suite

---

## 4. Setup & Environment Variables

Copy `.env.example` in `backend/` to `.env`:

```powershell
cd backend
Copy-Item .env.example .env
```

### Required & Configurable Environment Variables (`backend/.env`)

```env
# Server Configuration
PROJECT_NAME="ResolveAI"
PORT=8000
HOST="127.0.0.1"
ENVIRONMENT="development"

# Role-Based Demo Authentication
ADMIN_USERNAME="admin_resolve"
ADMIN_PASSWORD="MapleFox47"
TESTER_USERNAME="tester_resolve"
TESTER_PASSWORD="OrbitPanda82"
SESSION_SECRET="resolveai-demo-secret-key-change-in-production"
COOKIE_SECURE=false

# Google Gemma / Gemini API (Optional for live LLM extraction; mock fallback included)
GEMMA_API_KEY=""
USE_MOCK_GEMMA_IF_NO_KEY=true

# n8n Automation Engine Webhook Target (Optional; simulated dispatch if offline)
N8N_WEBHOOK_URL=""
SIMULATE_N8N_IF_OFFLINE=true

# Cloudinary Evidence Storage (Backend only — never exposed to client)
CLOUDINARY_CLOUD_NAME=""
CLOUDINARY_API_KEY=""
CLOUDINARY_API_SECRET=""
CLOUDINARY_FOLDER_PREFIX="campus-problems"

# OpenCV Image Processing Limits
MAX_IMAGES_PER_CASE=4
MAX_IMAGE_BYTES=8388608
MAX_IMAGE_PIXELS=24000000
MAX_IMAGE_DIMENSION=1920
MIN_IMAGE_DIMENSION=48
BLUR_VARIANCE_THRESHOLD=18

# Notion Documentation & Test Results Synchronization (Backend only)
NOTION_API_KEY=""
NOTION_PARENT_PAGE_ID=""
NOTION_DATABASE_ID=""
NOTION_DOCUMENTATION_PAGE_ID=""
```

---

## 5. Local Run & Verification

### Backend Startup

```powershell
cd backend
python -m pip install -r requirements.txt
$env:PYTHONPATH="backend"
python -m pytest tests -v
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*API documentation available at `http://127.0.0.1:8000/docs`.*

### Streamlit Frontend Startup (Python / SaaS Dashboard)

In a second terminal:

```powershell
python -m pip install -r frontend/requirements.txt
streamlit run frontend/app.py
```
*Streamlit web app available at `http://localhost:8501`.*

### React / TypeScript Frontend Startup (Alternative)

```powershell
cd frontend
npm install
npm run build
npm run dev -- --port 3000
```
*Application available at `http://127.0.0.1:3000`.*

---

## 5.1 Streamlit Community Cloud Deployment

To deploy the Streamlit frontend to Streamlit Community Cloud:

1. **Repository Settings**:
   - **Repository**: Your GitHub repository (`ResolveAI-Complete`)
   - **Branch**: `main`
   - **Main file path**: `frontend/app.py`
2. **Environment Variables / Secrets (Streamlit Cloud)**:
   In Streamlit Cloud App Settings &rarr; Secrets:
   ```toml
   BACKEND_URL = "https://your-deployed-fastapi-backend.com/api/v1"
   ```
3. **Backend Deployment**:
   Deploy the FastAPI backend separately (e.g. on Google Cloud Run, Render, or Railway) with the environment variables from `backend/.env.example` (`CLOUDINARY_*`, `NOTION_*`, etc.). Ensure the backend URL is public and configured in Streamlit Cloud's `BACKEND_URL`.

---

## 6. Live Presentation & Evaluation Workflow

1. **Portal Selection**: Visit `http://127.0.0.1:3000`. Explore the three dedicated options (User, Admin, Testing).
2. **User Portal (Public)**:
   - Click **"Test Case 1: Unique Issue"** &rarr; Submit. Note Gemma classification and n8n direct assignment.
   - Attach a sample photo. Note OpenCV image decoding, sharpness metrics, and Cloudinary upload.
   - Click **"Track Ticket"** to verify live status tracking by Ticket Number without logging in.
3. **Admin Portal (Protected)**:
   - Click **"Admin Portal"** &rarr; Login with `admin_resolve` / `MapleFox47` (or click "Autofill Credentials").
   - View newly submitted complaints in Admin Triage.
   - Submit **"Test Case 2: Paraphrased Duplicate"** from User Portal. Inspect how Admin Triage flags it as `held_for_review` with mathematical similarity scores.
   - Open review modal to approve, merge, or reject with audit notes.
4. **Testing Portal (Protected)**:
   - Click **"Testing Portal"** &rarr; Login with `tester_resolve` / `OrbitPanda82`.
   - Inspect **n8n Workflow**: interactive graph, webhook payload, execution history.
   - Inspect **Benchmark & USP**: 92.7% Macro-F1, duplicate precision/recall, and ablation studies.
   - Inspect **Notion Docs**: Check Notion sync status and trigger live documentation sync.
5. **Session Persistence & Role Isolation**:
   - Refresh the browser: active sessions persist via HTTP-only cookies.
   - Try navigating to Admin features with a Tester session: access is strictly blocked (403 Forbidden).

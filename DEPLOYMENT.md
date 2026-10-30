# 🚀 Production Deployment Guide: Render (Backend) + Vercel (Frontend)

This guide covers deploying **ResolveAI** with:
- **Backend**: FastAPI web service hosted on [Render](https://render.com)
- **Frontend**: React + Vite SPA hosted on [Vercel](https://vercel.com)

---

## Part 1: Deploy Backend to Render

### Option A: 1-Click Blueprint (Recommended)
Because this repository contains [`render.yaml`](render.yaml), you can deploy automatically:
1. Log into [Render Dashboard](https://dashboard.render.com).
2. Click **New +** &rarr; **Blueprint**.
3. Connect your GitHub repository: `https://github.com/shivamkrj65-star/ResolveAI`.
4. Render will parse `render.yaml` and configure the web service automatically.
5. In the environment variables section, fill in your secret API keys:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`
   - `NOTION_API_KEY`
   - `NOTION_PARENT_PAGE_ID`
   - `GEMMA_API_KEY` (optional)
   - `N8N_WEBHOOK_URL` (optional)
6. Click **Apply**.

---

### Option B: Manual Web Service Setup on Render
1. In Render, click **New +** &rarr; **Web Service**.
2. Connect your repository `ResolveAI`.
3. Configure the settings:
   - **Name**: `resolveai-backend`
   - **Region**: Any (e.g., Oregon or Frankfurt)
   - **Branch**: `main`
   - **Root Directory**: *(Leave blank)*
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Under **Advanced &rarr; Health Check Path**, enter: `/health`.
5. Under **Environment Variables**, add:
   | Key | Example / Value | Description |
   | :--- | :--- | :--- |
   | `PYTHON_VERSION` | `3.11.9` | Recommended Python runtime |
   | `ENVIRONMENT` | `production` | Production environment flag |
   | `COOKIE_SECURE` | `true` | Secure HTTPS cookie handling |
   | `CLOUDINARY_CLOUD_NAME` | `your_cloud_name` | Cloudinary Cloud Name |
   | `CLOUDINARY_API_KEY` | `your_api_key` | Cloudinary API Key |
   | `CLOUDINARY_API_SECRET` | `your_api_secret` | Cloudinary API Secret |
   | `NOTION_API_KEY` | `ntn_...` | Notion Internal Integration Secret |
   | `NOTION_PARENT_PAGE_ID`| `your_page_uuid` | Notion Page or Database ID |
   | `ADMIN_USERNAME` | `admin_resolve` | Admin Demo Username |
   | `ADMIN_PASSWORD` | `MapleFox47` | Admin Demo Password |
   | `TESTER_USERNAME` | `tester_resolve` | Tester Demo Username |
   | `TESTER_PASSWORD` | `OrbitPanda82` | Tester Demo Password |
   | `SESSION_SECRET` | *(Generate a 32-char string)* | HMAC session signing key |
6. Click **Deploy Web Service**.
7. Once deployed, copy your Render URL, e.g.:
   `https://resolveai-backend.onrender.com`

---

## Part 2: Deploy Frontend to Vercel

1. Log into your [Vercel Dashboard](https://vercel.com).
2. Click **Add New...** &rarr; **Project**.
3. Import your GitHub repository: `shivamkrj65-star/ResolveAI`.
4. Configure the project settings:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click *Edit* and select `frontend` (or leave default since root `vercel.json` is configured).
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Under **Environment Variables**, add:
   | Key | Value |
   | :--- | :--- |
   | `VITE_API_BASE_URL` | `https://your-backend-name.onrender.com/api/v1` |
   *(Replace with your actual Render URL from Part 1, followed by `/api/v1`)*.
6. Click **Deploy**.

---

## Part 3: Verify the Live Deployment

1. Visit your Vercel URL (e.g. `https://resolveai.vercel.app`).
2. Test the **User Portal**:
   - Register a complaint with photo evidence.
   - Verify that the image uploads to Cloudinary and generates a ticket ID (e.g. `RES-2026-101`).
   - Track the ticket publicly using the ticket ID.
3. Test the **Admin Portal**:
   - Log in using `admin_resolve` / `MapleFox47`.
   - Verify that all submitted complaints load in Admin Triage.
   - Change a case status or approve/merge duplicate candidates.
4. Test the **Testing Portal**:
   - Log in using `tester_resolve` / `OrbitPanda82`.
   - Check backend health, verify Cloudinary status, and test Notion synchronization.

---

## 🔒 Security Best Practices Checklist
- [x] Plaintext `.env` files are excluded by `.gitignore` and never committed.
- [x] Secrets are only set in Render / Vercel cloud dashboard environment variables.
- [x] Bearer tokens and session headers are automatically attached on cross-domain requests.
- [x] CORS is configured to allow requests from any Vercel domain (`https://*.vercel.app`).
- [x] SPA client-side routing rewrites are configured in `vercel.json`.

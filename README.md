# PRIMO Audit Dashboard — Vercel + Render + Neon

This project is a rebuild of your original Dash apps (`app.py`,
`review_app.py`, `daily_missing_app.py`) as a modern 3-tier app:

```
┌─────────────────┐      HTTPS       ┌──────────────────┐      SQL      ┌──────────────┐
│  Next.js + React │  ───────────────▶│  FastAPI backend  │ ──────────────▶│ Neon Postgres │
│  (Vercel)        │ ◀───────────────  │  (Render)         │ ◀──────────────│ (your data)   │
└─────────────────┘   JSON over CORS  └──────────────────┘                └──────────────┘
```

- **Frontend** (`frontend/`): Next.js 14 + Tailwind + Recharts — 3 pages that
  mirror your old apps: Clinical Dashboard (`/`), Participant Review
  (`/review`), Daily Missing Visits (`/daily-missing`). Deployed on **Vercel**.
- **Backend** (`backend/`): FastAPI app exposing JSON endpoints that
  replicate the exact logic of your three Dash apps (KPIs, charts, tables).
  Deployed on **Render**.
- **Database**: **Neon** (serverless Postgres). Your CSVs are loaded once
  into 3 tables: `master_data`, `participant_roster`, `query_log`.

No seed data is generated — you load **your own** CSVs using the provided
script.

---

## 1. Create the Neon database

1. Go to https://neon.tech, sign in, and create a new project (e.g. `primo-audit-dashboard`).
2. In the Neon dashboard, open **Connection Details** and copy the
   **connection string**. It looks like:

   ```
   postgresql://USER:PASSWORD@ep-xxxx-xxxx.region.aws.neon.tech/dbname?sslmode=require
   ```

3. Keep this string handy — you'll use it as `DATABASE_URL` in both the
   loader script (step 3) and the Render backend (step 5).

---

## 2. Push this code to GitHub

```bash
cd audit-dashboard         # the folder you unzip this project into
git init
git add .
git commit -m "PRIMO audit dashboard: Next.js + FastAPI + Neon"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

> The repo contains **two deployable apps** in one repo: `backend/` and
> `frontend/`. Both Render and Vercel let you point a deployment at a
> sub-directory, so you don't need separate repos.

---

## 3. Load your CSV data into Neon

This step replaces "seeding" — it loads **your real dataset** into Postgres.
Run it locally (once, and again whenever you have a new data export).

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export DATABASE_URL="postgresql://USER:PASSWORD@ep-xxxx.neon.tech/dbname?sslmode=require"

python scripts/load_data.py \
  --master  "/path/to/01_master_clean_dataset_final.csv" \
  --roster  "/path/to/02_participant_roster.csv" \
  --query-log "/path/to/query_log.csv"
```

This creates 3 tables in Neon:
- `master_data` — your 600+ column dataset (one row per record), all columns
  stored as `TEXT`. The backend handles type conversion on the fly, exactly
  like the original `pd.read_csv(...)` did.
- `participant_roster` — `participant_id`, `participant_type`, `family_id`, etc.
- `query_log` — `Query_ID`, `Category`, `Form`, `Issue`, `Status`.

**To refresh with new data later**, just re-run the script (it replaces the
tables), then call:

```bash
curl -X POST https://<your-render-backend>.onrender.com/api/admin/refresh
```

(or just wait up to 5 minutes — the backend auto-refreshes its in-memory
cache every 5 minutes).

---

## 4. Test the backend locally (optional but recommended)

```bash
cd backend
export DATABASE_URL="postgresql://USER:PASSWORD@ep-xxxx.neon.tech/dbname?sslmode=require"
export ALLOWED_ORIGINS="*"
uvicorn app.main:app --reload --port 8000
```

Visit http://localhost:8000/api/health — you should see row counts for
`master_data`, `participant_roster`, and `query_log`.

Other useful endpoints:
- `GET /api/overview/filters`, `GET /api/overview/data`
- `GET /api/review/filters`, `GET /api/review/data`
- `GET /api/daily-missing/filters`, `GET /api/daily-missing/data`

---

## 5. Deploy the backend on Render

1. Go to https://render.com → **New +** → **Web Service**.
2. Connect your GitHub repo.
3. Render will detect `backend/render.yaml`. If it asks you to confirm the
   root directory, set it to `backend`.
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:$PORT`
4. Under **Environment**, add:
   - `DATABASE_URL` = your Neon connection string (from step 1)
   - `ALLOWED_ORIGINS` = `*` for now (you'll tighten this in step 7 once you
     have your Vercel URL)
5. Click **Create Web Service**. Once deployed, note the URL, e.g.
   `https://primo-audit-dashboard-api.onrender.com`.
6. Visit `https://<your-backend>.onrender.com/api/health` to confirm it can
   read from Neon.

> Render free-tier services sleep after inactivity — the first request after
> idling may take ~30–50 seconds while it wakes up. This is normal.

---

## 6. Deploy the frontend on Vercel

1. Go to https://vercel.com → **Add New** → **Project**.
2. Import the same GitHub repo.
3. Set **Root Directory** to `frontend`.
4. Vercel auto-detects Next.js — leave build/output settings as default.
5. Under **Environment Variables**, add:
   - `NEXT_PUBLIC_API_URL` = `https://<your-backend>.onrender.com` (no
     trailing slash, from step 5)
6. Click **Deploy**. Once done, you'll get a URL like
   `https://primo-audit-dashboard.vercel.app`.

---

## 7. Lock down CORS (recommended)

Once you have your Vercel URL, go back to Render → your backend service →
**Environment** → set:

```
ALLOWED_ORIGINS=https://primo-audit-dashboard.vercel.app
```

Save — Render will redeploy automatically. This restricts the API so only
your frontend can call it (browsers will block other origins).

---

## 8. Verify everything end-to-end

1. Open your Vercel URL.
2. **Clinical Dashboard** (`/`): KPIs, charts, and the query log table should
   populate from Neon via the Render API.
3. **Participant Review** (`/review`): pick a form/visit, check completion
   counts.
4. **Daily Missing Visits** (`/daily-missing`): adjust include/exclude visit
   filters and confirm the summary + table update.

If a page shows "Could not reach the backend API", double-check
`NEXT_PUBLIC_API_URL` in Vercel and `ALLOWED_ORIGINS`/`DATABASE_URL` in Render.

---

## Repository structure

```
audit-dashboard/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app + CORS + health/admin routes
│   │   ├── database.py        # SQLAlchemy engine (Neon)
│   │   ├── data_loader.py      # loads + caches data from Postgres
│   │   ├── transforms.py       # shared dashboard logic (form labels, events, etc.)
│   │   └── routers/
│   │       ├── overview.py     # /api/overview/*  (Clinical Dashboard)
│   │       ├── review.py       # /api/review/*    (Participant Review)
│   │       └── daily_missing.py# /api/daily-missing/* (Daily Missing Visits)
│   ├── scripts/load_data.py    # CSV -> Neon loader
│   ├── requirements.txt
│   ├── render.yaml
│   └── .env.example
└── frontend/
    ├── app/
    │   ├── layout.js            # shared nav/header
    │   ├── page.js               # Clinical Dashboard
    │   ├── review/page.js        # Participant Review
    │   └── daily-missing/page.js # Daily Missing Visits
    ├── components/               # KpiCard, Charts, DataTable, filters
    ├── lib/api.js                # fetch wrapper around the backend API
    ├── package.json
    └── .env.local.example
```

## Updating the dataset later

Whenever you receive a new data export:

```bash
cd backend
export DATABASE_URL="<your Neon connection string>"
python scripts/load_data.py --master <new_master.csv> --roster <new_roster.csv> --query-log <new_query_log.csv>
curl -X POST https://<your-backend>.onrender.com/api/admin/refresh
```

No redeploy needed on either Vercel or Render.

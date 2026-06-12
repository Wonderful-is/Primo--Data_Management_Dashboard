import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .data_loader import get_cache, refresh_cache
from .routers import overview, review, daily_missing

app = FastAPI(title="PRIMO Audit Dashboard API", version="1.0.0")

# Allow the Vercel frontend (and local dev) to call this API.
# Set ALLOWED_ORIGINS as a comma-separated list of origins in Render's
# environment variables, e.g.
#   ALLOWED_ORIGINS=https://your-app.vercel.app,http://localhost:3000
allowed_origins = os.environ.get("ALLOWED_ORIGINS", "*")
origins = [o.strip() for o in allowed_origins.split(",")] if allowed_origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(overview.router)
app.include_router(review.router)
app.include_router(daily_missing.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "PRIMO Audit Dashboard API is running"}


@app.get("/api/health")
def health():
    try:
        cache = get_cache()
        return {
            "status": "ok",
            "rows_master": int(len(cache["data"])),
            "rows_roster": int(len(cache["roster"])),
            "rows_query_log": int(len(cache["query_log"])),
            "loaded_at": cache["loaded_at"],
        }
    except Exception as exc:  # pragma: no cover
        return {"status": "error", "detail": str(exc)}


@app.post("/api/admin/refresh")
def admin_refresh():
    """Re-load data from the database into memory.

    Call this after you load/update the CSV data in Neon so the API
    reflects the new data without needing a redeploy.
    """
    loaded_at = refresh_cache()
    return {"status": "ok", "loaded_at": loaded_at}

"""
Loads the master dataset, participant roster and query log from Postgres
(Neon) into pandas DataFrames, applies the shared transformations, and
caches the result in memory so every API request doesn't hit the DB.

Call `refresh_cache()` (e.g. via POST /api/admin/refresh) after you load
new data into the database so the API picks up the changes without a
redeploy.
"""

import threading
import time

import pandas as pd

from .database import engine
from . import transforms as t

_CACHE_LOCK = threading.Lock()
_CACHE = {
    "data": None,
    "roster": None,
    "query_log": None,
    "participant_base": None,
    "daily_review_base": None,
    "loaded_at": 0,
}

CACHE_TTL_SECONDS = 300  # auto-refresh every 5 minutes


def _load_from_db():
    data = pd.read_sql("SELECT * FROM master_data", engine)
    roster = pd.read_sql("SELECT * FROM participant_roster", engine)

    try:
        query_log = pd.read_sql("SELECT * FROM query_log", engine)
    except Exception:
        query_log = pd.DataFrame(columns=["Query_ID", "Category", "Form", "Issue", "Status"])

    data = t.prepare_master(data)
    participant_base = t.build_participant_base(data)
    daily_review_base = t.build_daily_review_base(data, roster)

    return {
        "data": data,
        "roster": roster,
        "query_log": query_log,
        "participant_base": participant_base,
        "daily_review_base": daily_review_base,
        "loaded_at": time.time(),
    }


def refresh_cache():
    with _CACHE_LOCK:
        _CACHE.update(_load_from_db())
    return _CACHE["loaded_at"]


def get_cache():
    with _CACHE_LOCK:
        is_empty = _CACHE["data"] is None
        is_stale = (time.time() - _CACHE["loaded_at"]) > CACHE_TTL_SECONDS

    if is_empty or is_stale:
        refresh_cache()

    return _CACHE

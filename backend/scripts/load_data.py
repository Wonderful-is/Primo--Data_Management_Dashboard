"""
One-off / repeatable script that loads your CSV dataset into Neon Postgres
so the FastAPI backend can serve it.

Usage (from the `backend/` directory):

    pip install -r requirements.txt
    export DATABASE_URL="postgresql://user:password@host/dbname?sslmode=require"

    python scripts/load_data.py \
        --master /path/to/01_master_clean_dataset_final.csv \
        --roster /path/to/02_participant_roster.csv \
        --query-log /path/to/query_log.csv

This will (re)create three tables:
    - master_data          (the big 600+ column dataset, one row per record)
    - participant_roster   (participant_id, participant_type, family_id, study_arm, ...)
    - query_log            (Query_ID, Category, Form, Issue, Status)

All columns are stored as TEXT. The backend (app/transforms.py) handles any
type conversion (dates, numeric checks, etc.) in pandas after loading, which
keeps this loader simple and avoids type-mismatch errors on ingest.

You can re-run this script any time you have a new data export - it replaces
the existing tables (`if_exists="replace"`), then call:

    POST https://<your-render-backend>/api/admin/refresh

(or just redeploy / wait 5 minutes for the in-memory cache to refresh)
so the API serves the new data.
"""

import argparse
import os
import sys

import pandas as pd
from sqlalchemy import create_engine, text


def load_csv_as_text(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, low_memory=False, dtype=str)
    # Normalize column names a little (Postgres lower-cases unquoted
    # identifiers anyway, and pandas to_sql will quote them, so keep as-is
    # but strip whitespace just in case).
    df.columns = [c.strip() for c in df.columns]
    return df


def main():
    parser = argparse.ArgumentParser(description="Load CSV dataset into Neon Postgres")
    parser.add_argument("--master", required=True, help="Path to 01_master_clean_dataset_final.csv")
    parser.add_argument("--roster", required=True, help="Path to 02_participant_roster.csv")
    parser.add_argument("--query-log", required=True, help="Path to query_log.csv")
    parser.add_argument(
        "--database-url",
        default=os.environ.get("DATABASE_URL"),
        help="Postgres connection string (defaults to $DATABASE_URL)",
    )
    parser.add_argument(
        "--chunksize",
        type=int,
        default=200,
        help="Rows per INSERT batch (lower this if you hit 'too many parameters' errors)",
    )
    args = parser.parse_args()

    if not args.database_url:
        print("ERROR: DATABASE_URL not set and --database-url not provided.", file=sys.stderr)
        sys.exit(1)

    engine = create_engine(args.database_url)

    print(f"Reading master dataset from {args.master} ...")
    master_df = load_csv_as_text(args.master)
    print(f"  -> {master_df.shape[0]} rows, {master_df.shape[1]} columns")

    print(f"Reading roster from {args.roster} ...")
    roster_df = load_csv_as_text(args.roster)
    print(f"  -> {roster_df.shape[0]} rows, {roster_df.shape[1]} columns")

    print(f"Reading query log from {args.query_log} ...")
    query_log_df = load_csv_as_text(args.query_log)
    print(f"  -> {query_log_df.shape[0]} rows, {query_log_df.shape[1]} columns")

    with engine.begin() as conn:
        print("Writing table: master_data ...")
        master_df.to_sql(
            "master_data",
            conn,
            if_exists="replace",
            index=False,
            chunksize=args.chunksize,
            method="multi",
        )

        print("Writing table: participant_roster ...")
        roster_df.to_sql(
            "participant_roster",
            conn,
            if_exists="replace",
            index=False,
            chunksize=args.chunksize,
            method="multi",
        )

        print("Writing table: query_log ...")
        query_log_df.to_sql(
            "query_log",
            conn,
            if_exists="replace",
            index=False,
            chunksize=args.chunksize,
            method="multi",
        )

        # Helpful indexes for filtering/joining.
        for stmt in [
            'CREATE INDEX IF NOT EXISTS idx_master_participant_id ON master_data ("participant_id")',
            'CREATE INDEX IF NOT EXISTS idx_master_family_id ON master_data ("family_id")',
            'CREATE INDEX IF NOT EXISTS idx_roster_participant_id ON participant_roster ("participant_id")',
        ]:
            try:
                conn.execute(text(stmt))
            except Exception as exc:  # pragma: no cover
                print(f"  (skipping index, column may not exist: {exc})")

    print("Done! Data loaded into Neon Postgres.")
    print("If your backend is already running, call POST /api/admin/refresh")
    print("(or wait up to 5 minutes) so it picks up the new data.")


if __name__ == "__main__":
    main()

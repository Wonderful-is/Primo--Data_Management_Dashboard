import os

from sqlalchemy import create_engine

DATABASE_URL = os.environ.get("DATABASE_URL", "")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL environment variable is not set. "
        "Set it to your Neon Postgres connection string, e.g. "
        "postgresql://user:password@host/dbname?sslmode=require"
    )

# Neon requires SSL. Most Neon connection strings already include
# `?sslmode=require`, but we make sure it's set just in case.
connect_args = {}
if "sslmode" not in DATABASE_URL:
    connect_args["sslmode"] = "require"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
    connect_args=connect_args,
)

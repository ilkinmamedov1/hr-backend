#!/usr/bin/env bash
set -e

echo "Waiting for database..."
python - <<'PY'
import time, sys
from sqlalchemy import create_engine, text
from app.core.config import settings

for attempt in range(60):
    try:
        engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Database is ready.")
        sys.exit(0)
    except Exception as exc:
        print(f"DB not ready ({attempt + 1}/60): {exc}")
        time.sleep(2)
print("Database did not become ready in time.", file=sys.stderr)
sys.exit(1)
PY

exec uvicorn app.main:app --host 0.0.0.0 --port 8000

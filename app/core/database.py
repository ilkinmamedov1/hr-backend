from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(bind=engine, autoflush=True, autocommit=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    import app.models  # noqa: F401  (register all models)

    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gist"))
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS ltree"))
        conn.commit()

    Base.metadata.create_all(bind=engine)

    with engine.begin() as conn:
        conn.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS token_version "
                "INTEGER NOT NULL DEFAULT 0"
            )
        )
        conn.execute(
            text(
                "ALTER TABLE timesheets ADD COLUMN IF NOT EXISTS daily_records_json "
                "JSONB NOT NULL DEFAULT '{}'::jsonb"
            )
        )

    ddl = """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint WHERE conname = 'no_overlapping_main_contract'
        ) THEN
            ALTER TABLE employment_contracts
            ADD CONSTRAINT no_overlapping_main_contract
            EXCLUDE USING gist (
                employee_id WITH =,
                daterange(start_date, COALESCE(end_date, 'infinity'::date), '[]') WITH &&
            ) WHERE (work_type = 'MAIN' AND status = 'ACTIVE');
        END IF;
    END $$;
    """
    with engine.begin() as conn:
        conn.execute(text(ddl))

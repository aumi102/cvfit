from sqlalchemy import inspect, text

from app.db.session import engine, Base


def init_db():
    # MVP compatibility: keep startup table creation until Alembic is wired into
    # every deployment path.
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)

    with engine.begin() as conn:
        inspector = inspect(conn)
        if "analysis_jobs" not in inspector.get_table_names():
            return
        column_names = {column["name"] for column in inspector.get_columns("analysis_jobs")}
        if "access_token_hash" not in column_names:
            # Temporary Phase 1B compatibility for databases created before the
            # Alembic baseline existed. Remove after migrations are mandatory.
            conn.execute(text("ALTER TABLE analysis_jobs ADD COLUMN access_token_hash VARCHAR(64)"))

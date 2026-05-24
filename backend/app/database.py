from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _column_exists(table: str, column: str) -> bool:
    insp = inspect(engine)
    if table not in insp.get_table_names():
        return False
    return column in {c["name"] for c in insp.get_columns(table)}


def migrate_db():
    migrations = [
        ("raw_articles", "title_zh", "VARCHAR(500)"),
        ("raw_articles", "summary_zh", "TEXT"),
        ("raw_articles", "title_original", "VARCHAR(500)"),
        ("raw_articles", "summary_original", "TEXT"),
        ("raw_articles", "category", "VARCHAR(50) DEFAULT 'news'"),
        ("raw_articles", "localized", "BOOLEAN DEFAULT FALSE"),
    ]
    with engine.connect() as conn:
        for table, column, col_type in migrations:
            if not _column_exists(table, column):
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {col_type}"))
                conn.commit()
        # PostgreSQL enum may predate agent_survey report type
        conn.execute(text("ALTER TYPE reporttype ADD VALUE IF NOT EXISTS 'agent_survey'"))
        conn.commit()
        # Agent survey reports are not tied to a single article
        conn.execute(text("ALTER TABLE reports ALTER COLUMN article_id DROP NOT NULL"))
        conn.commit()
        conn.execute(text("ALTER TYPE reporttype ADD VALUE IF NOT EXISTS 'daily_briefing'"))
        conn.commit()
        if not _column_exists("reports", "user_prompt"):
            conn.execute(text("ALTER TABLE reports ADD COLUMN user_prompt TEXT"))
            conn.commit()


def init_db():
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    migrate_db()

"""Clear article-related data and optionally re-run crawl pipeline."""
from __future__ import annotations

import argparse
import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import SessionLocal, init_db
from app.models import AgentTool, DailyBriefing, DailyBriefingItem, RawArticle, Report, SignalScore
from app.pipeline import run_full_pipeline


def purge_articles(db, *, keep_custom_reports: bool = True) -> dict:
    counts = {}

    counts["briefing_items"] = db.query(DailyBriefingItem).delete(synchronize_session=False)
    counts["briefings"] = db.query(DailyBriefing).delete(synchronize_session=False)
    counts["signals"] = db.query(SignalScore).delete(synchronize_session=False)

    db.query(AgentTool).update({AgentTool.article_id: None}, synchronize_session=False)

    if keep_custom_reports:
        counts["reports"] = (
            db.query(Report)
            .filter(Report.article_id.isnot(None))
            .delete(synchronize_session=False)
        )
    else:
        counts["reports"] = db.query(Report).delete(synchronize_session=False)

    counts["articles"] = db.query(RawArticle).delete(synchronize_session=False)
    db.commit()
    return counts


def main() -> int:
    parser = argparse.ArgumentParser(description="Reset articles and re-crawl")
    parser.add_argument("--purge-only", action="store_true", help="Only delete data, do not crawl")
    parser.add_argument("--all-reports", action="store_true", help="Delete all reports including custom")
    args = parser.parse_args()

    init_db()
    db = SessionLocal()
    try:
        counts = purge_articles(db, keep_custom_reports=not args.all_reports)
        print("Purged:", counts)
        if args.purge_only:
            return 0
        print("Running full pipeline (crawl + localize + score)...")
        result = asyncio.run(run_full_pipeline(db))
        print("Pipeline result:", result)
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())

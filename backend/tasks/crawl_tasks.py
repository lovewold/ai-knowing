from app.database import SessionLocal, init_db
from app.pipeline import run_full_pipeline_sync
from tasks.celery_app import celery_app


@celery_app.task(name="tasks.crawl_tasks.run_crawl_pipeline")
def run_crawl_pipeline():
    init_db()
    db = SessionLocal()
    try:
        result = run_full_pipeline_sync(db)
        print(f"[pipeline] completed: {result}")
        return result
    finally:
        db.close()

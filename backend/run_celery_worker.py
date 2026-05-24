"""PyCharm / local dev entry: Celery worker (Windows uses solo pool)."""
import sys

from celery.__main__ import main

if __name__ == "__main__":
    sys.argv = [
        "celery",
        "-A",
        "tasks.celery_app",
        "worker",
        "--loglevel=info",
        "--pool=solo",
    ]
    main()

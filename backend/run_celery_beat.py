"""PyCharm / local dev entry: Celery beat scheduler."""
import sys

from celery.__main__ import main

if __name__ == "__main__":
    sys.argv = [
        "celery",
        "-A",
        "tasks.celery_app",
        "beat",
        "--loglevel=info",
    ]
    main()

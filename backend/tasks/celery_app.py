from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery("aiknow", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)

# Parse cron: "0 */2 * * *" -> every 2 hours
_cron_parts = settings.crawl_cron.split()
if len(_cron_parts) == 5:
    minute, hour, _, _, _ = _cron_parts
    if hour.startswith("*/"):
        interval = int(hour[2:])
        celery_app.conf.beat_schedule = {
            "crawl-every-n-hours": {
                "task": "tasks.crawl_tasks.run_crawl_pipeline",
                "schedule": crontab(minute=minute, hour=f"*/{interval}"),
            }
        }
    else:
        celery_app.conf.beat_schedule = {
            "crawl-scheduled": {
                "task": "tasks.crawl_tasks.run_crawl_pipeline",
                "schedule": crontab(minute=minute, hour=hour),
            }
        }
else:
    celery_app.conf.beat_schedule = {
        "crawl-every-2-hours": {
            "task": "tasks.crawl_tasks.run_crawl_pipeline",
            "schedule": crontab(minute=0, hour="*/2"),
        }
    }


celery_app.autodiscover_tasks(["tasks"])

# autodiscover only loads tasks.py; register crawl_tasks explicitly
import tasks.crawl_tasks  # noqa: E402, F401

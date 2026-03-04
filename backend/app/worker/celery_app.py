"""
Celery application configuration.
Beat schedule: runs feed sync every 2 hours.
"""

import ssl

from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "cto_newsletter",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.worker.tasks"],
)

# ── Celery Config ──
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# ── Beat Schedule — Every 2 hours ──
celery_app.conf.beat_schedule = {
    "sync-all-feeds-every-2-hours": {
        "task": "app.worker.tasks.run_sync_cycle",
        "schedule": settings.FEED_SYNC_INTERVAL_HOURS * 3600,  # Convert hours to seconds
    },
}

# ── SSL for Upstash Redis (rediss://) ──
if settings.CELERY_BROKER_URL.startswith("rediss://"):
    celery_app.conf.broker_use_ssl = {"ssl_cert_reqs": ssl.CERT_NONE}
    celery_app.conf.redis_backend_use_ssl = {"ssl_cert_reqs": ssl.CERT_NONE}

"""
Celery application configuration for background task processing
"""

from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "document_processing",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.document_tasks",
        "app.tasks.ai_tasks",
        "app.tasks.workflow_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    result_expires=3600,  # 1 hour
    task_routes={
        "app.tasks.document_tasks.*": {"queue": "document_processing"},
        "app.tasks.ai_tasks.*": {"queue": "ai_processing"},
        "app.tasks.workflow_tasks.*": {"queue": "workflow_processing"},
    },
    task_annotations={
        "*": {"rate_limit": "10/s"},
        "app.tasks.ai_tasks.*": {"rate_limit": "5/s"},
    }
)

# Periodic tasks (Celery Beat)
celery_app.conf.beat_schedule = {
    "cleanup-old-jobs": {
        "task": "app.tasks.maintenance_tasks.cleanup_old_jobs",
        "schedule": 3600.0,  # Run every hour
    },
    "generate-daily-analytics": {
        "task": "app.tasks.analytics_tasks.generate_daily_analytics",
        "schedule": 86400.0,  # Run daily
    },
    "health-check": {
        "task": "app.tasks.maintenance_tasks.system_health_check",
        "schedule": 300.0,  # Run every 5 minutes
    },
}

if __name__ == "__main__":
    celery_app.start()

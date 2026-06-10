from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery('job_agent', broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.task_default_queue = 'job_agent'

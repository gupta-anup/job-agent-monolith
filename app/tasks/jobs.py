from __future__ import annotations

import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name='app.tasks.jobs.scrape_and_process_application', bind=True)
def scrape_and_process_application(self: object, job_id: str, app_id: str, target_url: str) -> dict[str, str]:
    logger.info('Queued scrape pipeline for job_id=%s app_id=%s target_url=%s', job_id, app_id, target_url)
    return {'job_id': job_id, 'app_id': app_id, 'target_url': target_url}

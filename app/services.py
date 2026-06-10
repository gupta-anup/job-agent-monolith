from __future__ import annotations

import logging

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ApplicationLog, ApplicationStatus, CandidateProfile, JobPosting
from app.schemas import JobScrapeRequest, ProfileUpsertRequest
from app.tasks.jobs import scrape_and_process_application

logger = logging.getLogger(__name__)


class ApplicationService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_profile(self, payload: ProfileUpsertRequest) -> CandidateProfile:
        try:
            query = select(CandidateProfile).where(CandidateProfile.full_name == payload.full_name)
            result = await self._session.execute(query)
            existing = result.scalar_one_or_none()
            if existing is not None:
                existing.master_resume = payload.master_resume
                await self._session.commit()
                await self._session.refresh(existing)
                return existing

            profile = CandidateProfile(full_name=payload.full_name, master_resume=payload.master_resume)
            self._session.add(profile)
            await self._session.commit()
            await self._session.refresh(profile)
            return profile
        except SQLAlchemyError as exc:
            await self._session.rollback()
            logger.exception('Profile upsert transaction failed for %s', payload.full_name)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Failed to persist candidate profile',
            ) from exc

    async def create_scrape_application(self, payload: JobScrapeRequest) -> ApplicationLog:
        try:
            job = JobPosting(url=payload.target_url)
            self._session.add(job)
            await self._session.flush()

            application = ApplicationLog(job_id=job.id, status=ApplicationStatus.pending)
            self._session.add(application)
            await self._session.commit()
            await self._session.refresh(application)
        except SQLAlchemyError as exc:
            await self._session.rollback()
            logger.exception('Failed creating application record for %s', payload.target_url)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Failed to create application log',
            ) from exc

        try:
            scrape_and_process_application.delay(str(job.id), str(application.id), payload.target_url)
        except Exception as exc:
            logger.exception('Failed to enqueue celery task for app_id=%s', application.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Failed to enqueue scraping task',
            ) from exc

        return application

    async def get_application_status(self, app_id: str) -> ApplicationLog:
        try:
            application = await self._session.get(ApplicationLog, app_id)
        except SQLAlchemyError as exc:
            logger.exception('Failed loading application status for app_id=%s', app_id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Failed to query application status',
            ) from exc

        if application is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Application not found')
        return application

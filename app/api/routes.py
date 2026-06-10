from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas import (
    ApiResponse,
    ApplicationStatusResponse,
    JobScrapeRequest,
    JobScrapeResponse,
    ProfileResponse,
    ProfileUpsertRequest,
)
from app.services import ApplicationService

router = APIRouter(prefix='/api/v1')


async def get_application_service(session: AsyncSession = Depends(get_db_session)) -> ApplicationService:
    return ApplicationService(session)


@router.post('/jobs/scrape', response_model=ApiResponse[JobScrapeResponse], status_code=status.HTTP_202_ACCEPTED)
async def scrape_jobs(
    payload: JobScrapeRequest,
    service: ApplicationService = Depends(get_application_service),
) -> ApiResponse[JobScrapeResponse]:
    application = await service.create_scrape_application(payload)
    return ApiResponse(
        data=JobScrapeResponse(app_id=application.id, job_id=application.job_id, status=application.status),
    )


@router.get(
    '/applications/{app_id}/status',
    response_model=ApiResponse[ApplicationStatusResponse],
    status_code=status.HTTP_200_OK,
)
async def get_application_status(
    app_id: str,
    service: ApplicationService = Depends(get_application_service),
) -> ApiResponse[ApplicationStatusResponse]:
    application = await service.get_application_status(app_id)
    return ApiResponse(
        data=ApplicationStatusResponse(
            id=application.id,
            job_id=application.job_id,
            status=application.status,
            tailored_resume_path=application.tailored_resume_path,
            updated_at=application.updated_at,
        )
    )


@router.post('/profiles', response_model=ApiResponse[ProfileResponse], status_code=status.HTTP_201_CREATED)
async def upsert_profile(
    payload: ProfileUpsertRequest,
    service: ApplicationService = Depends(get_application_service),
) -> ApiResponse[ProfileResponse]:
    profile = await service.upsert_profile(payload)
    return ApiResponse(
        data=ProfileResponse(
            id=profile.id,
            full_name=profile.full_name,
            master_resume=profile.master_resume,
            created_at=profile.created_at,
        )
    )

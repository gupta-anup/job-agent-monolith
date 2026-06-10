from __future__ import annotations

from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, Field

from app.db.models import ApplicationStatus


class JobScrapeRequest(BaseModel):
    target_url: str = Field(min_length=1)


class ProfileUpsertRequest(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    master_resume: dict[str, Any]


class ProfileResponse(BaseModel):
    id: UUID
    full_name: str
    master_resume: dict[str, Any]
    created_at: datetime


class JobScrapeResponse(BaseModel):
    app_id: UUID
    job_id: UUID
    status: ApplicationStatus


class ApplicationStatusResponse(BaseModel):
    id: UUID
    job_id: UUID
    status: ApplicationStatus
    tailored_resume_path: str | None
    updated_at: datetime


T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    data: T

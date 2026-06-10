from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ApplicationStatus(str, enum.Enum):
    pending = 'pending'
    tailoring = 'tailoring'
    applying = 'applying'
    success = 'success'
    failed = 'failed'


class CandidateProfile(Base):
    __tablename__ = 'candidate_profile'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    master_resume: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class JobPosting(Base):
    __tablename__ = 'job_postings'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False, default='Unknown title')
    company: Mapped[str] = mapped_column(String(255), nullable=False, default='Unknown company')
    raw_jd: Mapped[str] = mapped_column(Text, nullable=False, default='')
    url: Mapped[str] = mapped_column(String(1024), nullable=False)

    applications: Mapped[list[ApplicationLog]] = relationship(back_populates='job', cascade='all, delete-orphan')


class ApplicationLog(Base):
    __tablename__ = 'application_logs'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey('job_postings.id', ondelete='CASCADE'))
    status: Mapped[ApplicationStatus] = mapped_column(
        Enum(ApplicationStatus, name='application_status', native_enum=True),
        nullable=False,
        default=ApplicationStatus.pending,
    )
    tailored_resume_path: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    job: Mapped[JobPosting] = relationship(back_populates='applications')

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.routes import get_application_service
from app.db.models import ApplicationStatus
from app.main import app
from app.schemas import JobScrapeRequest, ProfileUpsertRequest


class FakeProfile:
    def __init__(self, full_name: str, master_resume: dict[str, object]) -> None:
        self.id = uuid4()
        self.full_name = full_name
        self.master_resume = master_resume
        self.created_at = datetime.now(tz=timezone.utc)


class FakeApplication:
    def __init__(self, status: ApplicationStatus) -> None:
        self.id = uuid4()
        self.job_id = uuid4()
        self.status = status
        self.tailored_resume_path = None
        self.updated_at = datetime.now(tz=timezone.utc)


class FakeService:
    expected_target_url = 'https://example.com/jobs/1'

    async def upsert_profile(self, payload: ProfileUpsertRequest) -> FakeProfile:
        return FakeProfile(payload.full_name, payload.master_resume)

    async def create_scrape_application(self, payload: JobScrapeRequest) -> FakeApplication:
        assert payload.target_url == self.expected_target_url
        return FakeApplication(ApplicationStatus.pending)

    async def get_application_status(self, app_id: str) -> FakeApplication:
        assert app_id
        return FakeApplication(ApplicationStatus.tailoring)


def override_service() -> FakeService:
    return FakeService()


def test_upsert_profile_endpoint() -> None:
    app.dependency_overrides[get_application_service] = override_service
    client = TestClient(app)

    response = client.post(
        '/api/v1/profiles',
        json={'full_name': 'Anup Gupta', 'master_resume': {'skills': ['python', 'sql']}},
    )

    assert response.status_code == 201
    body = response.json()
    assert body['data']['full_name'] == 'Anup Gupta'
    assert body['data']['master_resume']['skills'] == ['python', 'sql']


def test_scrape_endpoint_returns_pending_status() -> None:
    app.dependency_overrides[get_application_service] = override_service
    client = TestClient(app)

    response = client.post('/api/v1/jobs/scrape', json={'target_url': 'https://example.com/jobs/1'})

    assert response.status_code == 202
    assert response.json()['data']['status'] == 'pending'


def test_get_application_status_endpoint() -> None:
    app.dependency_overrides[get_application_service] = override_service
    client = TestClient(app)

    response = client.get(f"/api/v1/applications/{uuid4()}/status")

    assert response.status_code == 200
    assert response.json()['data']['status'] == 'tailoring'

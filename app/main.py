from __future__ import annotations

import logging

from fastapi import FastAPI

from app.api.routes import router
from app.core.config import get_settings

settings = get_settings()
logging.basicConfig(level=logging.INFO)

app = FastAPI(title=settings.app_name)
app.include_router(router)


@app.get('/healthz')
async def health_check() -> dict[str, str]:
    return {'status': 'ok'}

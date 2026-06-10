from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'AI Job Application Agent'
    api_prefix: str = '/api/v1'
    database_url: str = Field(
        default='postgresql+asyncpg://localhost:5432/job_agent',
        alias='DATABASE_URL',
    )
    redis_url: str = Field(default='redis://localhost:6379/0', alias='REDIS_URL')
    smtp_host: str = Field(default='localhost', alias='SMTP_HOST')
    smtp_port: int = Field(default=25, alias='SMTP_PORT')
    smtp_use_tls: bool = Field(default=False, alias='SMTP_USE_TLS')
    smtp_username: str | None = Field(default=None, alias='SMTP_USERNAME')
    smtp_password: str | None = Field(default=None, alias='SMTP_PASSWORD')


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

from __future__ import annotations

import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass(slots=True)
class ExecutionPayload:
    application_url: str
    resume_path: Path
    email: str | None = None


class ExecutionError(RuntimeError):
    pass


async def execute_application(payload: ExecutionPayload) -> None:
    if payload.email:
        _send_application_email(payload.email, payload.resume_path, settings.smtp_host, settings.smtp_port)
        return

    browser = None
    context = None
    page = None
    playwright = None
    try:
        from playwright.async_api import async_playwright

        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(payload.application_url, wait_until='domcontentloaded')
        await page.set_input_files("input[type='file']", str(payload.resume_path))
    except Exception as exc:
        logger.exception('Failed browser-based execution for %s', payload.application_url)
        raise ExecutionError('Failed to execute browser application flow') from exc
    finally:
        if page is not None:
            await page.close()
        if context is not None:
            await context.close()
        if browser is not None:
            await browser.close()
        if playwright is not None:
            await playwright.stop()


def _send_application_email(target_email: str, resume_path: Path, smtp_host: str, smtp_port: int) -> None:
    try:
        message = EmailMessage()
        message['Subject'] = 'Job Application'
        message['To'] = target_email
        message.set_content('Please find my tailored resume attached.')
        message.add_attachment(
            resume_path.read_bytes(),
            maintype='application',
            subtype='pdf',
            filename=resume_path.name,
        )

        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as smtp:
            smtp.send_message(message)
    except Exception as exc:
        logger.exception('Failed SMTP dispatch to %s', target_email)
        raise ExecutionError(f'Failed to send application email: {exc}') from exc

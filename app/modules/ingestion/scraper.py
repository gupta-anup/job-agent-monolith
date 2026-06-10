from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ScrapedJobData:
    title: str
    company: str
    raw_jd: str
    url: str
    hr_email: str | None = None


class IngestionError(RuntimeError):
    pass


async def scrape_job_posting(target_url: str, timeout_ms: int = 30_000) -> ScrapedJobData:
    browser = None
    context = None
    page = None
    playwright = None
    try:
        from playwright.async_api import TimeoutError as PlaywrightTimeoutError
        from playwright.async_api import async_playwright

        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(target_url, wait_until='domcontentloaded', timeout=timeout_ms)
        title = await page.title()
        raw_jd = await page.locator('body').inner_text()

        return ScrapedJobData(
            title=title or 'Unknown title',
            company='Unknown company',
            raw_jd=raw_jd,
            url=target_url,
        )
    except PlaywrightTimeoutError as exc:
        logger.exception('Playwright timeout while scraping %s', target_url)
        raise IngestionError('Scraping timed out') from exc
    except Exception as exc:
        logger.exception('Failed to scrape target url: %s', target_url)
        raise IngestionError('Failed to scrape job posting') from exc
    finally:
        if page is not None:
            await page.close()
        if context is not None:
            await context.close()
        if browser is not None:
            await browser.close()
        if playwright is not None:
            await playwright.stop()

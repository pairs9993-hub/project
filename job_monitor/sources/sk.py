from __future__ import annotations

from playwright.sync_api import BrowserContext

from ..config import Settings
from ..models import JobPosting
from ..utils import compact_text, extract_tail_id


class SkCareersSource:
    name = "sk_careers"
    listing_url = "https://www.skcareers.com/Recruit"

    _CARD_SCRIPT = """
    elements => elements.map((el) => ({
        title: el.querySelector('.title')?.textContent?.trim() || '',
        url: el.querySelector('a.list-link.url')?.href || '',
        company: el.querySelector('.company')?.textContent?.trim() || '',
        role: el.querySelector('.jobRole')?.textContent?.trim() || '',
        workingType: el.querySelector('.workingType')?.textContent?.trim() || '',
        recruitType: el.querySelector('.recruitType')?.textContent?.trim() || '',
        workingArea: el.querySelector('.workingArea')?.textContent?.trim() || '',
        period: el.querySelector('.date')?.textContent?.trim() || '',
        dDay: el.querySelector('.d-day')?.textContent?.trim() || '',
    }))
    """

    def collect(self, context: BrowserContext, settings: Settings) -> list[JobPosting]:
        page = context.new_page()
        try:
            page.goto(self.listing_url, wait_until="networkidle", timeout=45000)
            self._expand_all(page)
            items = page.locator("#RecruitList .list-item").evaluate_all(self._CARD_SCRIPT)
            return [self._to_job(item) for item in items if compact_text(item.get("url"))]
        finally:
            page.close()

    def _expand_all(self, page) -> None:
        button = page.locator(".btnMoSearch")
        previous_count = -1

        for _ in range(15):
            current_count = page.locator("#RecruitList .list-item").count()
            if current_count == previous_count:
                break
            previous_count = current_count

            if not button.is_visible():
                break

            button.scroll_into_view_if_needed()
            button.click()
            page.wait_for_timeout(1500)

    def _to_job(self, item: dict) -> JobPosting:
        url = compact_text(item.get("url"))
        tags = [
            compact_text(item.get("role")),
            compact_text(item.get("workingType")),
            compact_text(item.get("recruitType")),
            compact_text(item.get("workingArea")),
        ]
        tags = [tag for tag in tags if tag]

        return JobPosting(
            source=self.name,
            external_id=extract_tail_id(url),
            company=compact_text(item.get("company")),
            title=compact_text(item.get("title")),
            url=url,
            experience_level=compact_text(item.get("recruitType")),
            employment_type=compact_text(item.get("workingType")),
            location=compact_text(item.get("workingArea")),
            job_function=compact_text(item.get("role")),
            posted_range=compact_text(item.get("period")),
            d_day=compact_text(item.get("dDay")),
            tags=tags,
            summary=" / ".join(tags),
        )
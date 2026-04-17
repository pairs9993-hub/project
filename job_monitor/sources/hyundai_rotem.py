from __future__ import annotations

import re

from playwright.sync_api import BrowserContext

from ..config import Settings
from ..models import JobPosting
from ..utils import compact_text


class HyundaiRotemSource:
    name = "hyundai_rotem"
    listing_url = "https://hyundai-rotem.recruiter.co.kr/career/home"

    _CARD_SCRIPT = """
    elements => elements.map((el) => {
        const paragraphs = Array.from(el.querySelectorAll('p')).map(node => node.textContent.trim()).filter(Boolean);
        const labels = paragraphs.slice(3);
        return {
            url: el.href,
            status: el.querySelector('span')?.textContent?.trim() || '',
            title: paragraphs[0] || '',
            period: paragraphs.slice(1, 3).join(' ').trim(),
            labels,
        };
    })
    """

    def collect(self, context: BrowserContext, settings: Settings) -> list[JobPosting]:
        page = context.new_page()
        try:
            page.goto(self.listing_url, wait_until="networkidle", timeout=45000)
            items = page.locator("a[href*='/career/jobs/']").evaluate_all(self._CARD_SCRIPT)
            return [self._to_job(item) for item in items if compact_text(item.get("url"))]
        finally:
            page.close()

    def _to_job(self, item: dict) -> JobPosting:
        url = compact_text(item.get("url"))
        match = re.search(r"/career/jobs/(\d+)", url)
        external_id = match.group(1) if match else url
        labels = [compact_text(label) for label in item.get("labels", []) if compact_text(label)]
        title = compact_text(item.get("title"))
        combined = " ".join([title, *labels])

        employment_type = "계약" if "계약" in combined else "정규"
        experience_level = labels[0] if labels else ""

        return JobPosting(
            source=self.name,
            external_id=external_id,
            company="현대로템",
            title=title,
            url=url,
            experience_level=experience_level,
            employment_type=employment_type,
            posted_range=compact_text(item.get("period")),
            tags=labels,
            summary=" / ".join(labels),
            metadata={"status": compact_text(item.get("status"))},
        )
from __future__ import annotations

from playwright.sync_api import BrowserContext

from ..config import Settings
from ..models import JobPosting
from ..utils import compact_text


class SamsungCareersSource:
    name = "samsung_careers"
    listing_url = "https://www.samsungcareers.com/hr/?ty=B"

    _CARD_SCRIPT = r"""
    elements => elements.map((el) => ({
        dataValue: el.querySelector('a[data-value]')?.getAttribute('data-value') || '',
        company: el.querySelector('.company')?.textContent?.trim() || '',
        title: el.querySelector('.title')?.textContent?.trim() || '',
        info: Array.from(el.querySelectorAll('.info span')).map(node => node.textContent.trim()).filter(Boolean),
        flags: Array.from(el.querySelectorAll('.flagWrap .flag.grey')).map(node => node.textContent.trim()).filter(Boolean),
        dDay: el.querySelector('.flagWrap .flag.blue')?.textContent?.replace(/\s+/g, ' ').trim() || '',
    }))
    """

    def collect(self, context: BrowserContext, settings: Settings) -> list[JobPosting]:
        page = context.new_page()
        try:
            page.goto(self.listing_url, wait_until="networkidle", timeout=45000)
            items = page.locator("#list > li").evaluate_all(self._CARD_SCRIPT)
            return [self._to_job(item) for item in items if compact_text(item.get("dataValue"))]
        finally:
            page.close()

    def _to_job(self, item: dict) -> JobPosting:
        data_value = compact_text(item.get("dataValue")).replace(",", "")
        title = compact_text(item.get("title"))
        flags = [compact_text(flag) for flag in item.get("flags", []) if compact_text(flag)]
        condition_text = " ".join([title, *flags])
        employment_type = "계약" if any(keyword in condition_text for keyword in ("계약직", "계약")) else "정규"
        info = [compact_text(value) for value in item.get("info", []) if compact_text(value)]

        return JobPosting(
            source=self.name,
            external_id=data_value,
            company=compact_text(item.get("company")),
            title=title,
            url=f"https://www.samsungcareers.com/hr/?no={data_value}",
            experience_level=info[0] if info else "",
            employment_type=employment_type,
            posted_range=info[1] if len(info) > 1 else "",
            d_day=compact_text(item.get("dDay")),
            tags=flags,
            summary=" / ".join(flags),
        )
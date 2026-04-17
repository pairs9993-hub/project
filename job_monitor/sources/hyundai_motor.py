from __future__ import annotations

import math

from playwright.sync_api import BrowserContext

from ..config import Settings
from ..models import JobPosting
from ..utils import calculate_d_day, compact_text, format_yyyymmdd


class HyundaiMotorSource:
    name = "hyundai_motor"
    listing_url = "https://talent.hyundai.com/apply/applyList.hc"

    _FETCH_SCRIPT = """
    async ({ pageNo }) => {
        const vita = sessionStorage.getItem('vita') || '';
        const params = new URLSearchParams({
            hgrCd: '1',
            lang: 'ko',
            page: String(pageNo),
            pageblock: '10',
            searchFieldList: '',
            searchOccupList: '',
            searchPlaceList: '',
            searchSectorList: '',
            searchText: '',
            jdSec: '',
            srcOrd: '',
            intnsvYn: ''
        });

        const response = await fetch('/api/rec/AP-HM-FO-02700?' + params.toString(), {
            headers: {
                'X-HKMC-TOKEN': vita,
                'X-HKMC-SERVICE': 'HM'
            }
        });

        return await response.json();
    }
    """

    def collect(self, context: BrowserContext, settings: Settings) -> list[JobPosting]:
        page = context.new_page()
        try:
            page.goto(self.listing_url, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(2500)

            first_payload = page.evaluate(self._FETCH_SCRIPT, {"pageNo": 1})
            if first_payload.get("status") != 200:
                raise RuntimeError(f"Hyundai Motor API returned {first_payload.get('status')}")

            first_data = first_payload["data"]
            total_count = int(first_data["listCnt"])
            total_pages = max(1, math.ceil(total_count / 10))
            raw_items = list(first_data["list"])

            for page_no in range(2, total_pages + 1):
                payload = page.evaluate(self._FETCH_SCRIPT, {"pageNo": page_no})
                if payload.get("status") != 200:
                    raise RuntimeError(f"Hyundai Motor page {page_no} failed")
                raw_items.extend(payload["data"]["list"])

            return [self._to_job(item, settings.timezone) for item in raw_items]
        finally:
            page.close()

    def _to_job(self, item: dict, timezone: str) -> JobPosting:
        recu_type = compact_text(item.get("recuType"))
        experience_map = {
            "N1": "신입",
            "N2": "경력",
            "N3": "인턴",
            "N4": "기타",
            "N5": "계약",
        }
        employment_map = {
            "N1": "정규",
            "N2": "정규",
            "N3": "인턴",
            "N4": "기타",
            "N5": "계약",
        }

        title = compact_text(item.get("recuNoticeNm"))
        url = (
            "https://talent.hyundai.com/apply/applyView.hc"
            f"?recuYy={item.get('recuYy')}&recuType={item.get('recuType')}&recuCls={item.get('recuCls')}"
        )
        tags = [
            compact_text(item.get("secCodeNm")),
            compact_text(item.get("fldCodeNm")),
            compact_text(item.get("workPlaceCodeNm")),
            compact_text(item.get("channelCodeNm")),
        ]
        tags = [tag for tag in tags if tag]

        start_date = format_yyyymmdd(item.get("applyStartDt"))
        end_date = format_yyyymmdd(item.get("applyEndDt"))
        posted_range = f"{start_date} ~ {end_date}".strip(" ~")

        return JobPosting(
            source=self.name,
            external_id=f"{item.get('recuYy')}-{item.get('recuType')}-{item.get('recuCls')}",
            company="현대자동차",
            title=title,
            url=url,
            experience_level=experience_map.get(recu_type, compact_text(item.get("channelCodeNm"))),
            employment_type=employment_map.get(recu_type, ""),
            location=compact_text(item.get("workPlaceCodeNm")),
            category=compact_text(item.get("secCodeNm")),
            job_function=compact_text(item.get("fldCodeNm")),
            posted_range=posted_range,
            d_day=calculate_d_day(item.get("applyEndDt"), timezone),
            tags=tags,
            summary=" / ".join(tags),
            metadata={
                "recu_type": recu_type,
                "recu_cls": str(item.get("recuCls")),
            },
        )
from __future__ import annotations

from dataclasses import dataclass
from html import escape

import requests

from .models import JobPosting
from .utils import chunk_lines, html_link


SOURCE_LABELS = {
    "hyundai_motor": "현대자동차",
    "hyundai_rotem": "현대로템",
    "sk_careers": "SK Careers",
    "samsung_careers": "삼성 커리어스",
}


class NotificationError(RuntimeError):
    pass


@dataclass(slots=True)
class TelegramNotifier:
    bot_token: str
    chat_id: str

    def send_jobs(self, jobs: list[JobPosting]) -> None:
        if not jobs:
            return

        lines = [f"<b>새 채용공고 {len(jobs)}건</b>"]
        for job in jobs:
            label = SOURCE_LABELS.get(job.source, job.source)
            condition = " / ".join(
                value for value in [job.experience_level, job.employment_type, job.location] if value
            )
            summary = " / ".join(job.tags[:4]) if job.tags else job.summary

            lines.append("")
            lines.append(f"<b>[{escape(label)}]</b> {escape(job.company)}")
            lines.append(escape(job.title))
            if condition:
                lines.append(escape(condition))
            if summary:
                lines.append(escape(summary))
            lines.append(html_link("공고 보기", job.url))

        for message in chunk_lines(lines):
            response = requests.post(
                f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": False,
                },
                timeout=20,
            )
            if response.status_code >= 400:
                raise NotificationError(response.text)

    def send_status(self, message: str) -> None:
        response = requests.post(
            f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
            json={
                "chat_id": self.chat_id,
                "text": message,
            },
            timeout=20,
        )
        if response.status_code >= 400:
            raise NotificationError(response.text)
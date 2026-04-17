from __future__ import annotations

from .config import Settings
from .models import JobPosting
from .utils import contains_keyword, normalize_text


def _is_career(job: JobPosting) -> bool:
    value = normalize_text(" ".join([job.experience_level, job.title, *job.tags]))

    if "신입/경력" in value or "new/experienced" in value or "무관" in value:
        return False

    return any(
        keyword in value
        for keyword in ("경력", "experienced", "career", "experienced hire")
    )


def _is_regular(job: JobPosting) -> bool:
    value = normalize_text(" ".join([job.employment_type, job.title, *job.tags]))

    if any(keyword in value for keyword in ("계약", "계약직", "contract", "아르바이트", "intern", "인턴", "기타")):
        return False

    return any(keyword in value for keyword in ("정규", "regular", "경력", "experienced", "일반채용"))


def _is_sw_related(job: JobPosting, settings: Settings) -> bool:
    value = job.search_blob

    if any(contains_keyword(value, keyword) for keyword in settings.exclude_keywords):
        return False

    return any(contains_keyword(value, keyword) for keyword in settings.include_keywords)


def is_relevant(job: JobPosting, settings: Settings) -> bool:
    return _is_career(job) and _is_regular(job) and _is_sw_related(job, settings)
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from html import escape
from typing import Iterable
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


TIMEZONE_FALLBACKS = {
    "Asia/Seoul": timezone(timedelta(hours=9)),
}


def compact_text(value: str | None) -> str:
    if not value:
        return ""
    return " ".join(value.split())


def normalize_text(value: str | None) -> str:
    return compact_text(value).lower()


def contains_keyword(text: str, keyword: str) -> bool:
    normalized_text = normalize_text(text)
    normalized_keyword = normalize_text(keyword)

    if not normalized_keyword:
        return False

    if re.fullmatch(r"[a-z0-9+#]{1,3}", normalized_keyword):
        pattern = rf"(?<![a-z0-9]){re.escape(normalized_keyword)}(?![a-z0-9])"
        return re.search(pattern, normalized_text) is not None

    return normalized_keyword in normalized_text


def extract_tail_id(url: str) -> str:
    stripped = url.rstrip("/")
    return stripped.rsplit("/", 1)[-1]


def format_yyyymmdd(value: str | None) -> str:
    if not value:
        return ""
    digits = re.sub(r"[^0-9]", "", value)
    if len(digits) != 8:
        return compact_text(value)
    return f"{digits[0:4]}.{digits[4:6]}.{digits[6:8]}"


def calculate_d_day(date_text: str | None, timezone: str) -> str:
    if not date_text:
        return ""

    digits = re.sub(r"[^0-9]", "", date_text)
    if len(digits) != 8:
        return ""

    target = datetime.strptime(digits, "%Y%m%d").date()
    today = now_in_timezone(timezone).date()

    delta = (target - today).days
    if delta == 0:
        return "D-Day"
    if delta > 0:
        return f"D-{delta}"
    return f"D+{abs(delta)}"


def html_link(label: str, url: str) -> str:
    return f'<a href="{escape(url, quote=True)}">{escape(label)}</a>'


def now_in_timezone(timezone_name: str) -> datetime:
    try:
        return datetime.now(ZoneInfo(timezone_name))
    except ZoneInfoNotFoundError:
        fallback = TIMEZONE_FALLBACKS.get(timezone_name)
        if fallback is None:
            return datetime.now().astimezone()
        return datetime.now(fallback)


def chunk_lines(lines: Iterable[str], limit: int = 3500) -> list[str]:
    chunks: list[str] = []
    current: list[str] = []
    current_length = 0

    for line in lines:
        extra = len(line) + 1
        if current and current_length + extra > limit:
            chunks.append("\n".join(current))
            current = [line]
            current_length = len(line)
            continue

        current.append(line)
        current_length += extra

    if current:
        chunks.append("\n".join(current))

    return chunks
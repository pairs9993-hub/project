from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT_DIR / ".env"

load_dotenv(ENV_FILE)


DEFAULT_SOURCES = (
    "hyundai_motor",
    "hyundai_rotem",
    "sk_careers",
    "samsung_careers",
)

DEFAULT_INCLUDE_KEYWORDS = (
    "sw",
    "software",
    "소프트웨어",
    "it",
    "ai",
    "ml",
    "data",
    "backend",
    "frontend",
    "server",
    "mobile",
    "android",
    "ios",
    "app",
    "application",
    "full stack",
    "fullstack",
    "platform",
    "플랫폼",
    "middleware",
    "system",
    "시스템",
    "robotics",
    "로보틱스",
    "agent",
    "embedded",
    "firmware",
    "security",
    "보안",
    "cloud",
    "infra",
    "infrastructure",
    "sap",
    "erp",
    "mes",
    "db",
    "service platform",
    "perception",
)

DEFAULT_EXCLUDE_KEYWORDS = (
    "사업개발",
    "영업",
    "마케팅",
    "재무",
    "회계",
    "총무",
    "인사",
    "품질",
    "생산",
    "구매",
    "설비",
    "시공",
    "안전",
    "상담",
    "패션",
    "vmd",
    "투자",
    "planner",
    "기획",
    "planning",
)


def _parse_csv(value: str | None, default: tuple[str, ...]) -> tuple[str, ...]:
    if value is None or not value.strip():
        return default

    items = [item.strip() for item in value.split(",")]
    return tuple(item for item in items if item)


def _parse_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


@dataclass(slots=True)
class Settings:
    root_dir: Path
    state_file: Path
    timezone: str
    enabled_sources: tuple[str, ...]
    include_keywords: tuple[str, ...]
    exclude_keywords: tuple[str, ...]
    telegram_bot_token: str | None
    telegram_chat_id: str | None
    always_notify: bool


def load_settings() -> Settings:
    state_file = Path(os.getenv("STATE_FILE", ROOT_DIR / "data" / "seen_jobs.json"))

    return Settings(
        root_dir=ROOT_DIR,
        state_file=state_file,
        timezone=os.getenv("TIMEZONE", "Asia/Seoul"),
        enabled_sources=_parse_csv(os.getenv("ENABLED_SOURCES"), DEFAULT_SOURCES),
        include_keywords=_parse_csv(os.getenv("INCLUDE_KEYWORDS"), DEFAULT_INCLUDE_KEYWORDS),
        exclude_keywords=_parse_csv(os.getenv("EXCLUDE_KEYWORDS"), DEFAULT_EXCLUDE_KEYWORDS),
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN") or None,
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID") or None,
        always_notify=_parse_bool(os.getenv("ALWAYS_NOTIFY"), default=False),
    )
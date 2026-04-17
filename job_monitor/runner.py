from __future__ import annotations

import logging
from dataclasses import dataclass, field

from playwright.sync_api import sync_playwright

from .config import Settings
from .filtering import is_relevant
from .models import JobPosting
from .notifiers import TelegramNotifier
from .sources import get_collectors
from .state import StateStore
from .utils import compact_text, now_in_timezone


LOGGER = logging.getLogger(__name__)

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)


@dataclass(slots=True)
class RunSummary:
    collected_count: int
    matched_count: int
    new_jobs: list[JobPosting] = field(default_factory=list)
    seeded: bool = False
    dry_run: bool = False
    errors: list[str] = field(default_factory=list)


def _now_iso(settings: Settings) -> str:
    return now_in_timezone(settings.timezone).isoformat(timespec="seconds")


def _build_notifier(settings: Settings) -> TelegramNotifier | None:
    if not settings.telegram_bot_token or not settings.telegram_chat_id:
        return None
    return TelegramNotifier(settings.telegram_bot_token, settings.telegram_chat_id)


def run_monitor(
    settings: Settings,
    *,
    dry_run: bool = False,
    include_existing: bool = False,
    source_names: tuple[str, ...] | None = None,
) -> RunSummary:
    if source_names:
        enabled_sources = source_names
    else:
        enabled_sources = settings.enabled_sources

    collectors = get_collectors(enabled_sources)
    state = StateStore(settings.state_file)
    errors: list[str] = []
    all_jobs: list[JobPosting] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            locale="ko-KR",
            timezone_id=settings.timezone,
            user_agent=DEFAULT_USER_AGENT,
            viewport={"width": 1440, "height": 1200},
        )

        try:
            for collector in collectors:
                try:
                    jobs = collector.collect(context, settings)
                    all_jobs.extend(jobs)
                    LOGGER.info("Collected %s jobs from %s", len(jobs), collector.name)
                except Exception as exc:  # noqa: BLE001
                    message = f"{collector.name}: {exc}"
                    errors.append(message)
                    LOGGER.exception("Collector failed: %s", collector.name)
        finally:
            context.close()
            browser.close()

    if not all_jobs and errors:
        raise RuntimeError("All sources failed: " + "; ".join(errors))

    matched_jobs = [job for job in all_jobs if is_relevant(job, settings)]
    matched_jobs.sort(key=lambda job: (job.source, compact_text(job.company), compact_text(job.title)))
    new_jobs = [job for job in matched_jobs if not state.has_seen(job)]
    now_iso = _now_iso(settings)

    if state.is_empty and not include_existing:
        if not dry_run:
            for job in all_jobs:
                state.touch(job, now_iso)
            state.save(now_iso)
        return RunSummary(
            collected_count=len(all_jobs),
            matched_count=len(matched_jobs),
            new_jobs=[],
            seeded=True,
            dry_run=dry_run,
            errors=errors,
        )

    if not dry_run:
        for job in all_jobs:
            state.touch(job, now_iso)
        state.save(now_iso)

    if new_jobs and not dry_run:
        notifier = _build_notifier(settings)
        if notifier is None:
            raise RuntimeError("New jobs were found but Telegram secrets are not configured.")
        notifier.send_jobs(new_jobs)
    elif not new_jobs and settings.always_notify and not dry_run:
        notifier = _build_notifier(settings)
        if notifier is not None:
            notifier.send_status("오늘은 새로 올라온 조건 일치 공고가 없습니다.")

    return RunSummary(
        collected_count=len(all_jobs),
        matched_count=len(matched_jobs),
        new_jobs=new_jobs,
        seeded=False,
        dry_run=dry_run,
        errors=errors,
    )
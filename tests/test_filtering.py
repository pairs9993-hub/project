from pathlib import Path

from job_monitor.config import DEFAULT_EXCLUDE_KEYWORDS, DEFAULT_INCLUDE_KEYWORDS, Settings
from job_monitor.filtering import is_relevant
from job_monitor.models import JobPosting


def build_settings() -> Settings:
    return Settings(
        root_dir=Path("."),
        state_file=Path("data/seen_jobs.json"),
        timezone="Asia/Seoul",
        enabled_sources=("hyundai_motor",),
        include_keywords=DEFAULT_INCLUDE_KEYWORDS,
        exclude_keywords=DEFAULT_EXCLUDE_KEYWORDS,
        telegram_bot_token=None,
        telegram_chat_id=None,
        always_notify=False,
    )


def test_sw_role_matches() -> None:
    job = JobPosting(
        source="hyundai_motor",
        external_id="1",
        company="현대자동차",
        title="Backend Engineer",
        url="https://example.com/jobs/1",
        experience_level="경력",
        employment_type="정규",
        category="IT",
        job_function="SW Development",
        tags=["IT", "Backend", "서울"],
    )

    assert is_relevant(job, build_settings()) is True


def test_planning_role_is_excluded() -> None:
    job = JobPosting(
        source="hyundai_motor",
        external_id="2",
        company="현대자동차",
        title="모빌리티 플랫폼 UX 기획",
        url="https://example.com/jobs/2",
        experience_level="경력",
        employment_type="정규",
        category="IT",
        job_function="Service Planning",
        tags=["IT", "플랫폼", "서울"],
    )

    assert is_relevant(job, build_settings()) is False


def test_contract_role_is_excluded() -> None:
    job = JobPosting(
        source="samsung_careers",
        external_id="3",
        company="삼성",
        title="AI Platform 개발",
        url="https://example.com/jobs/3",
        experience_level="경력",
        employment_type="계약",
        tags=["AI", "플랫폼"],
    )

    assert is_relevant(job, build_settings()) is False


def test_mixed_entry_level_role_is_excluded() -> None:
    job = JobPosting(
        source="hyundai_rotem",
        external_id="4",
        company="현대로템",
        title="로보틱스 SW 플랫폼 개발",
        url="https://example.com/jobs/4",
        experience_level="신입/경력",
        employment_type="정규",
        tags=["로보틱스", "SW"],
    )

    assert is_relevant(job, build_settings()) is False
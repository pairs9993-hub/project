from __future__ import annotations

import argparse
import logging

from .config import load_settings
from .runner import run_monitor


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="채용공고 모니터 실행기")
    parser.add_argument("--dry-run", action="store_true", help="알림과 상태 저장 없이 결과만 출력합니다.")
    parser.add_argument(
        "--include-existing",
        action="store_true",
        help="상태 파일이 비어 있어도 현재 조건 일치 공고를 신규로 간주합니다.",
    )
    parser.add_argument(
        "--source",
        action="append",
        dest="sources",
        help="특정 소스만 실행합니다. 예: --source hyundai_motor",
    )
    parser.add_argument("--verbose", action="store_true", help="디버그 로그를 출력합니다.")
    return parser


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s %(message)s")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    configure_logging(args.verbose)

    settings = load_settings()
    summary = run_monitor(
        settings,
        dry_run=args.dry_run,
        include_existing=args.include_existing,
        source_names=tuple(args.sources or []),
    )

    print(f"총 수집: {summary.collected_count}건")
    print(f"조건 일치: {summary.matched_count}건")
    print(f"신규 공고: {len(summary.new_jobs)}건")

    if summary.seeded:
        print("초기 실행이라 현재 공고를 상태 파일에만 저장했습니다. 다음 실행부터 새 공고만 알립니다.")

    if summary.new_jobs:
        for job in summary.new_jobs:
            print(f"- [{job.source}] {job.title} :: {job.url}")

    if summary.errors:
        print("수집 중 일부 오류가 있었습니다:")
        for error in summary.errors:
            print(f"- {error}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
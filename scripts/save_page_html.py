from __future__ import annotations

from pathlib import Path

from playwright.sync_api import sync_playwright


TARGETS = {
    "hyundai_motor_jobs": "https://talent.hyundai.com/apply/applyList.hc",
    "samsung_careers": "https://www.samsungcareers.com/hr/?ty=B",
    "hyundai_rotem_jobs": "https://hyundai-rotem.recruiter.co.kr/career/home",
    "sk_careers": "https://www.skcareers.com/Recruit",
}


def main() -> None:
    output_dir = Path("debug")
    output_dir.mkdir(exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(locale="ko-KR")

        for name, url in TARGETS.items():
            page = context.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            page.wait_for_timeout(5000)
            (output_dir / f"{name}.html").write_text(page.content(), encoding="utf-8")
            page.close()

        browser.close()


if __name__ == "__main__":
    main()
from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


TARGETS = {
    "hyundai_motor": "https://talent.hyundai.com/",
    "hyundai_motor_jobs": "https://talent.hyundai.com/apply/applyList.hc",
    "sk_careers": "https://www.skcareers.com/Recruit",
    "samsung_careers": "https://www.samsungcareers.com/hr/?ty=B",
    "hyundai_rotem_corp": "https://www.hyundai-rotem.co.kr/",
    "hyundai_rotem_jobs": "https://hyundai-rotem.recruiter.co.kr/appsite/company/index",
}


def compact(value: str) -> str:
    return " ".join(value.split())


def main() -> None:
    output_dir = Path("debug")
    output_dir.mkdir(exist_ok=True)
    summary: dict[str, dict[str, object]] = {}

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(locale="ko-KR")

        for name, url in TARGETS.items():
            page = context.new_page()
            result: dict[str, object] = {"requested_url": url}

            try:
                response = page.goto(url, wait_until="domcontentloaded", timeout=45000)
                page.wait_for_timeout(5000)
                result["final_url"] = page.url
                result["status"] = response.status if response else None
                result["title"] = page.title()

                anchors = []
                seen_pairs: set[tuple[str, str]] = set()
                for handle in page.locator("a").element_handles()[:80]:
                    text = compact(handle.inner_text())
                    href = handle.get_attribute("href") or ""
                    if not text and not href:
                        continue
                    pair = (text, href)
                    if pair in seen_pairs:
                        continue
                    seen_pairs.add(pair)
                    anchors.append({"text": text[:200], "href": href})
                result["anchors"] = anchors[:40]

                body_text = compact(page.locator("body").inner_text())
                result["body_excerpt"] = body_text[:4000]

                page.screenshot(path=str(output_dir / f"{name}.png"), full_page=True)
            except PlaywrightTimeoutError as exc:
                result["error"] = f"timeout: {exc}"
            except Exception as exc:  # noqa: BLE001
                result["error"] = repr(exc)
            finally:
                summary[name] = result
                page.close()

        browser.close()

    (output_dir / "site_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
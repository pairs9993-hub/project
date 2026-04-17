from __future__ import annotations

from typing import Protocol

from playwright.sync_api import BrowserContext

from ..config import Settings
from ..models import JobPosting


class SourceCollector(Protocol):
    name: str

    def collect(self, context: BrowserContext, settings: Settings) -> list[JobPosting]:
        ...
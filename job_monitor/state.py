from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .models import JobPosting


DEFAULT_STATE = {
    "schema_version": 1,
    "last_run_at": None,
    "jobs": {},
}


@dataclass(slots=True)
class StateStore:
    path: Path
    data: dict = field(init=False)

    def __post_init__(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data = self._load()

    def _load(self) -> dict:
        if not self.path.exists():
            return dict(DEFAULT_STATE)

        with self.path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    @property
    def is_empty(self) -> bool:
        return not self.data.get("jobs")

    def has_seen(self, job: JobPosting) -> bool:
        return job.job_id in self.data["jobs"]

    def touch(self, job: JobPosting, seen_at: str) -> None:
        entry = self.data["jobs"].get(job.job_id)
        if entry is None:
            self.data["jobs"][job.job_id] = {
                "source": job.source,
                "external_id": job.external_id,
                "company": job.company,
                "title": job.title,
                "url": job.url,
                "first_seen_at": seen_at,
                "last_seen_at": seen_at,
            }
            return

        entry["last_seen_at"] = seen_at
        entry["title"] = job.title
        entry["company"] = job.company
        entry["url"] = job.url

    def save(self, last_run_at: str) -> None:
        self.data["last_run_at"] = last_run_at
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(self.data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
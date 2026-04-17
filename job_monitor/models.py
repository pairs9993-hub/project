from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class JobPosting:
    source: str
    external_id: str
    company: str
    title: str
    url: str
    experience_level: str = ""
    employment_type: str = ""
    location: str = ""
    category: str = ""
    job_function: str = ""
    posted_range: str = ""
    d_day: str = ""
    tags: list[str] = field(default_factory=list)
    summary: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def job_id(self) -> str:
        return f"{self.source}:{self.external_id}"

    @property
    def search_blob(self) -> str:
        parts = [
            self.company,
            self.title,
            self.experience_level,
            self.employment_type,
            self.location,
            self.category,
            self.job_function,
            self.posted_range,
            self.summary,
            *self.tags,
        ]

        for value in self.metadata.values():
            if isinstance(value, str):
                parts.append(value)

        return " ".join(part for part in parts if part)
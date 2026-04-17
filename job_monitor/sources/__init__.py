from __future__ import annotations

from .base import SourceCollector
from .hyundai_motor import HyundaiMotorSource
from .hyundai_rotem import HyundaiRotemSource
from .samsung import SamsungCareersSource
from .sk import SkCareersSource


SOURCE_REGISTRY: dict[str, SourceCollector] = {
    HyundaiMotorSource.name: HyundaiMotorSource(),
    HyundaiRotemSource.name: HyundaiRotemSource(),
    SamsungCareersSource.name: SamsungCareersSource(),
    SkCareersSource.name: SkCareersSource(),
}


def get_collectors(enabled_sources: tuple[str, ...]) -> list[SourceCollector]:
    missing = [source for source in enabled_sources if source not in SOURCE_REGISTRY]
    if missing:
        raise ValueError(f"Unknown sources: {', '.join(missing)}")
    return [SOURCE_REGISTRY[source] for source in enabled_sources]
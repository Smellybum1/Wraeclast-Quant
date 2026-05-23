from __future__ import annotations

from typing import TypeAlias

from wraeclast_quant.collectors.base import Collector
from wraeclast_quant.collectors.build_sites import BuildSiteCollector
from wraeclast_quant.collectors.patch_notes import PatchNotesCollector
from wraeclast_quant.collectors.price_sites import PriceSiteCollector
from wraeclast_quant.collectors.social import SocialCollector
from wraeclast_quant.collectors.youtube import YouTubeCollector
from wraeclast_quant.config.resources_loader import Resource

CollectorType: TypeAlias = type[Collector]

COLLECTOR_REGISTRY: dict[str, CollectorType] = {
    "price_site": PriceSiteCollector,
    "build_site": BuildSiteCollector,
    "social": SocialCollector,
    "youtube": YouTubeCollector,
    "official": PatchNotesCollector,
    "patch_notes": PatchNotesCollector,
    "unknown": Collector,
}


def collector_for(resource: Resource) -> Collector:
    collector_cls = COLLECTOR_REGISTRY.get(resource.type, Collector)
    return collector_cls(resource)

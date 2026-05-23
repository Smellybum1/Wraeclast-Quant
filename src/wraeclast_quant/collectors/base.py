from __future__ import annotations

from pydantic import BaseModel

from wraeclast_quant.config.resources_loader import Resource


class CollectionResult(BaseModel):
    resource_name: str
    resource_type: str
    collector: str
    status: str
    message: str = ""


class Collector:
    def __init__(self, resource: Resource) -> None:
        self.resource = resource

    def collect(self, dry_run: bool) -> CollectionResult:
        status = "dry-run" if dry_run else "placeholder"
        return CollectionResult(
            resource_name=self.resource.name,
            resource_type=self.resource.type,
            collector=self.__class__.__name__,
            status=status,
            message="External collection is disabled in the MVP.",
        )


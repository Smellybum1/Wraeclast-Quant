from __future__ import annotations

from wraeclast_quant.config.resources_loader import Resource


def find_resource(name_or_id: str, resources: list[Resource]) -> Resource | None:
    normalized = name_or_id.strip().casefold()
    for resource in resources:
        if resource.name.strip().casefold() == normalized:
            return resource
        if resource.id and resource.id.strip().casefold() == normalized:
            return resource
    return None


def slug(value: str) -> str:
    return "_".join(
        part
        for part in "".join(
            character.lower() if character.isalnum() else " "
            for character in value
        ).split()
        if part
    )

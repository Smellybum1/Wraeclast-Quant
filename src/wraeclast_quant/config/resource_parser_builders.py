from __future__ import annotations

from wraeclast_quant.config.resource_models import Resource
from wraeclast_quant.config.resource_type_inference import infer_resource_type


def build_resource(data: dict[str, str], section: str) -> Resource:
    url = data.get("url", "")
    name = data.get("name") or _name_from_url(url) or "Unnamed resource"
    resource_type = data.get("type") or infer_resource_type(section, url, name)
    return Resource(
        id=(data.get("id") or "").strip(),
        name=name.strip(),
        url=url.strip(),
        type=resource_type.strip() or "unknown",
        priority=(data.get("priority") or "medium").strip() or "medium",
        allowed_use=(data.get("allowed_use") or "manual-review").strip() or "manual-review",
        collector=(data.get("collector") or "").strip(),
        refresh=(data.get("refresh") or "").strip(),
        reliability=(data.get("reliability") or "unknown").strip() or "unknown",
        notes=(data.get("notes") or "").strip(),
        section=section.strip(),
    )


def _name_from_url(url: str) -> str:
    if not url:
        return ""
    return url.removeprefix("https://").removeprefix("http://").split("/")[0]

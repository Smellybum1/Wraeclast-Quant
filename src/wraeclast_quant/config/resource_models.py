from __future__ import annotations

from pydantic import BaseModel


class Resource(BaseModel):
    id: str = ""
    name: str
    url: str = ""
    type: str = "unknown"
    priority: str = "medium"
    allowed_use: str = "manual-review"
    collector: str = ""
    refresh: str = ""
    reliability: str = "unknown"
    notes: str = ""
    section: str = ""


__all__ = ["Resource"]

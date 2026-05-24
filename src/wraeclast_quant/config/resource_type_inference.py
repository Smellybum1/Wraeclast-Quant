from __future__ import annotations


def infer_resource_type(section: str = "", url: str = "", name: str = "") -> str:
    text = f"{section} {url} {name}".lower()
    if "price" in text or "economy" in text or "poe2scout" in text:
        return "price_site"
    if "build" in text or "maxroll" in text or "mobalytics" in text:
        return "build_site"
    if "reddit" in text or "social" in text:
        return "social"
    if "youtube" in text or "video" in text:
        return "youtube"
    if "official" in text or "patch" in text or "pathofexile.com/forum" in text:
        return "official"
    return "unknown"


__all__ = ["infer_resource_type"]

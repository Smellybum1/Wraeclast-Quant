from wraeclast_quant.normalizers.text import normalize_whitespace


def normalize_item_name(name: str) -> str:
    cleaned = normalize_whitespace(name)
    cleaned = cleaned.replace("’", "'").replace("`", "'")
    return cleaned.title()


def normalize_item_key(name: str) -> str:
    return normalize_item_name(name).lower().replace(" ", "-").replace("'", "")


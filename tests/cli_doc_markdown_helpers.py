from __future__ import annotations


def documented_bullet_list(doc_text: str, heading: str) -> list[str]:
    section = doc_text.split(f"{heading}\n\n", 1)[1].split("\n\n", 1)[0]
    return [
        line.strip()[3:-1]
        for line in section.splitlines()
        if line.strip().startswith("- `")
    ]


def documented_bullets(doc_text: str, heading: str) -> set[str]:
    return set(documented_bullet_list(doc_text, heading))


def documented_status_row_keys(doc_text: str) -> list[str]:
    documented_keys_section = doc_text.split("Current row keys:\n\n", 1)[1].split(
        "\n\n", 1
    )[0]
    return [
        line.strip()[3:-1]
        for line in documented_keys_section.splitlines()
        if line.strip().startswith("- `")
    ]


__all__ = [
    "documented_bullet_list",
    "documented_bullets",
    "documented_status_row_keys",
]

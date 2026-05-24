from __future__ import annotations


def documented_bullets(doc_text: str, heading: str) -> set[str]:
    section = doc_text.split(f"{heading}\n\n", 1)[1].split("\n\n", 1)[0]
    return {
        line.strip()[3:-1]
        for line in section.splitlines()
        if line.strip().startswith("- `")
    }

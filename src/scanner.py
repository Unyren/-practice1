from __future__ import annotations

from pathlib import Path
from typing import Iterator


def scan(root_path: Path, exclude_patterns: list[str] | None = None) -> Iterator[Path]:
    exclude_patterns = exclude_patterns or []
    for path in root_path.rglob("*.mp3"):
        normalized_path = str(path)
        if any(pattern and pattern in normalized_path for pattern in exclude_patterns):
            continue
        yield path

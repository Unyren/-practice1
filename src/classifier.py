from __future__ import annotations

import re
from pathlib import Path
import unicodedata

from .config import OrganizeConfig
from .tag_reader import TagInfo

INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def _sanitize_component(value: str) -> str:
    # Normalize Unicode to NFC to avoid composed/decomposed form issues
    value = unicodedata.normalize("NFC", value)
    value = INVALID_CHARS.sub("_", value)
    value = value.strip()
    if not value:
        return "unknown"
    return value


def build_target_path(tag_info: TagInfo, config: OrganizeConfig) -> Path:
    placeholders = {
        "genre": _sanitize_component(tag_info.genre or config.fallback_dir),
        "artist": _sanitize_component(tag_info.artist or config.fallback_dir),
        "album": _sanitize_component(tag_info.album or config.fallback_dir),
    }
    try:
        relative_path = config.template.format(**placeholders)
    except KeyError as exc:
        raise ValueError(f"Invalid template placeholder: {exc}") from exc

    normalized = Path(*[ _sanitize_component(part) for part in Path(relative_path).parts ])
    if normalized.parts:
        return normalized
    return Path(config.fallback_dir)

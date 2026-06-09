from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError

from .exceptions import TagReadError


@dataclass
class TagInfo:
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    error: Optional[str] = None

    @property
    def has_required_fields(self) -> bool:
        return bool(self.artist and self.genre)


def _normalize_tag(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    clean = value.strip()
    return clean or None


def read_tags(mp3_path: Path) -> TagInfo:
    try:
        tags = EasyID3(mp3_path)
    except ID3NoHeaderError:
        return TagInfo(error="ID3 header missing")
    except Exception as exc:
        raise TagReadError(f"Failed to read tags for {mp3_path}: {exc}") from exc

    artist = _normalize_tag(tags.get("artist", [None])[0])
    album = _normalize_tag(tags.get("album", [None])[0])
    genre = _normalize_tag(tags.get("genre", [None])[0])

    return TagInfo(artist=artist, album=album, genre=genre)

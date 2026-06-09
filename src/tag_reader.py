from __future__ import annotations

import re
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


MOJIBAKE_RE = re.compile(r'[\u0080-\u00ff]')
HANGUL_RE = re.compile(r'[\uac00-\ud7a3]')


def _looks_like_mojibake(value: str) -> bool:
    return bool(MOJIBAKE_RE.search(value))


def _decode_cp949(value: str) -> str:
    for enc in ("latin-1", "cp1252", "iso-8859-1"):
        try:
            decoded = value.encode(enc).decode("cp949")
        except UnicodeError:
            continue
        if HANGUL_RE.search(decoded):
            return decoded
    return value


def _normalize_tag(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    clean = value.strip()
    if not clean:
        return None
    if _looks_like_mojibake(clean):
        clean = _decode_cp949(clean)
    return clean or None


def read_tags(mp3_path: Path) -> TagInfo:
    try:
        tags = EasyID3(mp3_path)
    except ID3NoHeaderError:
        return TagInfo(error="ID3 헤더 없음")
    except Exception as exc:
        raise TagReadError(f"태그 읽기 실패 {mp3_path}: {exc}") from exc

    artist = _normalize_tag(tags.get("artist", [None])[0])
    album = _normalize_tag(tags.get("album", [None])[0])
    genre = _normalize_tag(tags.get("genre", [None])[0])

    return TagInfo(artist=artist, album=album, genre=genre)

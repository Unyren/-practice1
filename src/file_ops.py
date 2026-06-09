from __future__ import annotations

import hashlib
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from .exceptions import DuplicateFileError, FileOperationError


@dataclass
class FileOperationResult:
    src: Path
    dst: Path
    status: str
    message: str


def _hash_file(path: Path) -> str:
    hasher = hashlib.md5()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def _files_are_equal(first: Path, second: Path) -> bool:
    if first.stat().st_size != second.stat().st_size:
        return False
    return _hash_file(first) == _hash_file(second)


def _resolve_duplicate(dst: Path) -> Path:
    base = dst.stem
    suffix = dst.suffix
    parent = dst.parent
    counter = 1
    while True:
        candidate = parent / f"{base}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def transfer(
    src: Path,
    dst: Path,
    mode: str = "copy",
    duplicate_strategy: str = "rename",
    dry_run: bool = False,
    progress_callback: Callable[[str], None] | None = None,
) -> FileOperationResult:
    if src.resolve() == dst.resolve():
        return FileOperationResult(src=src, dst=dst, status="skipped", message="Source and destination are the same")

    ensure_directory(dst.parent)

    if dst.exists():
        if _files_are_equal(src, dst):
            return FileOperationResult(src=src, dst=dst, status="skipped", message="Duplicate file already exists")

        if duplicate_strategy == "skip":
            return FileOperationResult(src=src, dst=dst, status="skipped", message="Destination exists")
        if duplicate_strategy == "rename":
            dst = _resolve_duplicate(dst)
        elif duplicate_strategy == "overwrite":
            if not dry_run:
                dst.unlink()
    if progress_callback:
        progress_callback(f"Preparing {src.name} -> {dst}")

    if dry_run:
        return FileOperationResult(src=src, dst=dst, status="dry-run", message="Dry run: no file written")

    try:
        if mode == "copy":
            shutil.copy2(src, dst)
        else:
            shutil.move(src, dst)
    except Exception as exc:
        raise FileOperationError(f"Failed to transfer {src} to {dst}: {exc}") from exc

    return FileOperationResult(src=src, dst=dst, status=mode, message="Success")

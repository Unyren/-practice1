from __future__ import annotations

from pathlib import Path
from typing import Callable

from .config import OrganizeConfig
from .classifier import build_target_path
from .file_ops import FileOperationResult, transfer
from .logger import create_logger, summary_message
from .scanner import scan
from .tag_reader import TagInfo, read_tags


def _make_target_path(src: Path, tag_info: TagInfo, config: OrganizeConfig) -> Path:
    relative = build_target_path(tag_info, config)
    return config.destination / relative / src.name


def run_organizer(
    config: OrganizeConfig,
    progress_callback: Callable[[str], None] | None = None,
) -> dict[str, int]:
    logger = create_logger(config.destination, config.verbose)
    config.validate()

    summary = {
        "total": 0,
        "copied": 0,
        "moved": 0,
        "skipped": 0,
        "errors": 0,
    }

    for mp3_path in scan(config.source, config.exclude_patterns):
        summary["total"] += 1
        try:
            tag_info = read_tags(mp3_path)
            if tag_info.error or not tag_info.has_required_fields:
                if progress_callback:
                    progress_callback(f"⚠ 태그 누락: {mp3_path.name} (기본 폴더 사용)")
            target_path = _make_target_path(mp3_path, tag_info, config)
            result = transfer(
                src=mp3_path,
                dst=target_path,
                mode=config.mode,
                duplicate_strategy=config.duplicate_strategy,
                dry_run=config.dry_run,
                progress_callback=progress_callback,
            )

            if result.status == "copy":
                summary["copied"] += 1
                status_icon = "📋"
            elif result.status == "move":
                summary["moved"] += 1
                status_icon = "📂"
            else:
                summary["skipped"] += 1
                status_icon = "⏭️ "

            logger.info(f"{result.status.upper()}: {mp3_path} -> {result.dst} ({result.message})")
            if progress_callback:
                progress_callback(f"{status_icon} {result.status.upper()}: {mp3_path.name}")
        except Exception as exc:
            summary["errors"] += 1
            logger.exception(f"오류 발생: {mp3_path}: {exc}")
            if progress_callback:
                progress_callback(f"❌ 오류: {mp3_path.name} - {exc}")

    summary_line = summary_message(summary)
    logger.info(summary_line)
    if progress_callback:
        progress_callback("=" * 60)
        progress_callback(summary_line)
    return summary

from __future__ import annotations

import logging
from pathlib import Path


def create_logger(destination: Path, verbose: bool = False) -> logging.Logger:
    logger = logging.getLogger("mp3_organizer")
    logger.handlers.clear()
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    log_file = destination / "mp3_organizer.log"
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def summary_message(summary: dict[str, int]) -> str:
    return (
        f"Processed {summary['total']} files: copied={summary['copied']} moved={summary['moved']} "
        f"skipped={summary['skipped']} errors={summary['errors']}"
    )

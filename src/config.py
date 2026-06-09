from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class OrganizeConfig:
    source: Path
    destination: Path
    mode: str = "copy"
    template: str = "genre/{genre}/{artist}"
    fallback_dir: str = "unknown"
    duplicate_strategy: str = "rename"
    dry_run: bool = False
    exclude_patterns: list[str] = field(default_factory=list)
    workers: int = 1
    verbose: bool = False

    def validate(self) -> None:
        if self.mode not in {"copy", "move"}:
            raise ValueError("mode must be 'copy' or 'move'")
        if self.duplicate_strategy not in {"skip", "rename", "overwrite"}:
            raise ValueError("duplicate_strategy must be 'skip', 'rename', or 'overwrite'")
        if self.workers < 1:
            raise ValueError("workers must be at least 1")
        if not self.source.exists() or not self.source.is_dir():
            raise ValueError("source must be an existing directory")
        if not self.destination.exists():
            self.destination.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "OrganizeConfig":
        return cls(
            source=Path(data.get("source", ".")),
            destination=Path(data.get("destination", "./organized")),
            mode=data.get("mode", "copy"),
            template=data.get("template", "genre/{genre}/{artist}"),
            fallback_dir=data.get("fallback_dir", "unknown"),
            duplicate_strategy=data.get("duplicate_strategy", "rename"),
            dry_run=bool(data.get("dry_run", False)),
            exclude_patterns=list(data.get("exclude_patterns", [])),
            workers=int(data.get("workers", 1)),
            verbose=bool(data.get("verbose", False)),
        )

    @classmethod
    def load_json(cls, path: Path) -> "OrganizeConfig":
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        return cls.from_dict(data)

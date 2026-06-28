# Copyright (c) 2026 SoftSiliconX Pvt Ltd
# All rights reserved.
#
# File Name        : models.py
# File Description :
# Author           : Santhosh
# Date             : 2026-06-28

"""Shared data models."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any


class Operation(StrEnum):
    """A supported header operation."""

    ADD = "add"
    UPDATE = "update"
    REMOVE = "remove"
    VERIFY = "verify"
    PREVIEW = "preview"


class ResultStatus(StrEnum):
    """Outcome of processing one file."""

    ADDED = "added"
    UPDATED = "updated"
    REMOVED = "removed"
    VALID = "valid"
    MISSING = "missing"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass(slots=True)
class Config:
    """Resolved application configuration."""

    root: Path = field(default_factory=Path.cwd)
    company: str = "SoftSiliconX Pvt Ltd"
    author: str = ""
    year: int = 0
    description: str = ""
    template: str = "default"
    template_dir: Path | None = None
    use_gitignore: bool = True
    use_ssxignore: bool = True
    include: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    extensions: tuple[str, ...] = ()
    preserve_timestamps: bool = True
    report: str = "console"

    def __post_init__(self) -> None:
        self.root = self.root.resolve()
        if self.template_dir is not None:
            self.template_dir = self.template_dir.resolve()


@dataclass(slots=True, frozen=True)
class ScanEntry:
    """A file accepted by the repository scanner."""

    path: Path
    size: int
    is_symlink: bool = False


@dataclass(slots=True)
class ScanStatistics:
    """Scanner counters."""

    visited: int = 0
    accepted: int = 0
    ignored: int = 0
    binary: int = 0
    unsupported: int = 0
    symlinks: int = 0
    errors: int = 0


@dataclass(slots=True, frozen=True)
class ProcessResult:
    """Result for a single processed file."""

    path: Path
    status: ResultStatus
    changed: bool = False
    diff: str = ""
    error: str = ""

    def as_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation."""

        return {
            "path": str(self.path),
            "status": self.status.value,
            "changed": self.changed,
            "diff": self.diff,
            "error": self.error,
        }

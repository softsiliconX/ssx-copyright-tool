"""Lazy, read-only repository scanner."""

from __future__ import annotations

import os
from collections.abc import Callable, Iterator
from pathlib import Path

from .comments import comment_style
from .ignore import IgnoreEngine
from .models import ScanEntry, ScanStatistics

ProgressCallback = Callable[[Path, ScanStatistics], None]


class RepositoryScanner:
    """Scan supported text files without modifying repository contents."""

    def __init__(
        self,
        root: Path,
        *,
        ignore_engine: IgnoreEngine | None = None,
        extensions: tuple[str, ...] = (),
        follow_symlinks: bool = False,
        progress: ProgressCallback | None = None,
    ) -> None:
        self.root = root.resolve()
        self.ignore_engine = ignore_engine or IgnoreEngine(self.root)
        self.extensions = frozenset(
            extension.lower() if extension.startswith(".") else f".{extension.lower()}"
            for extension in extensions
        )
        self.follow_symlinks = follow_symlinks
        self.progress = progress
        self.statistics = ScanStatistics()

    @staticmethod
    def is_binary(path: Path, sample_size: int = 8192) -> bool:
        """Detect likely binary files using a small byte sample."""

        with path.open("rb") as stream:
            sample = stream.read(sample_size)
        if not sample:
            return False
        if b"\x00" in sample:
            return True
        control = sum(byte < 9 or 13 < byte < 32 for byte in sample)
        return control / len(sample) > 0.30

    def scan(self) -> Iterator[ScanEntry]:
        """Yield accepted files lazily while pruning ignored directories."""

        for current, directories, filenames in os.walk(
            self.root, followlinks=self.follow_symlinks
        ):
            directory = Path(current)
            self.ignore_engine.load_directory(directory)
            self.statistics.ignored += self.ignore_engine.prune(directory, directories)
            if not self.follow_symlinks:
                symlink_dirs = [name for name in directories if (directory / name).is_symlink()]
                self.statistics.symlinks += len(symlink_dirs)
                directories[:] = [name for name in directories if name not in symlink_dirs]
            for filename in filenames:
                path = directory / filename
                self.statistics.visited += 1
                try:
                    if path.is_symlink() and not self.follow_symlinks:
                        self.statistics.symlinks += 1
                        continue
                    if self.ignore_engine.ignored(path):
                        self.statistics.ignored += 1
                        continue
                    if self.extensions and path.suffix.lower() not in self.extensions:
                        self.statistics.unsupported += 1
                        continue
                    if comment_style(path) is None:
                        self.statistics.unsupported += 1
                        continue
                    if self.is_binary(path):
                        self.statistics.binary += 1
                        continue
                    stat = path.stat()
                except (OSError, PermissionError):
                    self.statistics.errors += 1
                    continue
                self.statistics.accepted += 1
                if self.progress:
                    self.progress(path, self.statistics)
                yield ScanEntry(path=path, size=stat.st_size, is_symlink=path.is_symlink())


Scanner = RepositoryScanner

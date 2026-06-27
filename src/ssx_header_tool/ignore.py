"""Cached Git-wildmatch ignore evaluation with nested ignore files."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pathspec

from .constants import DEFAULT_IGNORES


class IgnoreEngine:
    """Evaluate repository and nested ignore files."""

    def __init__(
        self,
        root: Path,
        *,
        use_gitignore: bool = True,
        use_ssxignore: bool = True,
        include: tuple[str, ...] = (),
        exclude: tuple[str, ...] = (),
    ) -> None:
        self.root = root.resolve()
        self.use_gitignore = use_gitignore
        self.use_ssxignore = use_ssxignore
        self.include_spec = (
            pathspec.PathSpec.from_lines("gitignore", include) if include else None
        )
        extra = [*DEFAULT_IGNORES, *exclude]
        self.base_spec = pathspec.PathSpec.from_lines("gitignore", extra)
        self._specs: dict[Path, pathspec.PathSpec[Any]] = {}
        self._loaded: set[Path] = set()
        self._cache: dict[Path, bool] = {}
        self.load_directory(self.root)

    @staticmethod
    def _read_rules(path: Path) -> list[str]:
        try:
            return path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError):
            return []

    def load_directory(self, directory: Path) -> None:
        """Load ignore rules declared directly in a directory."""

        directory = directory.resolve()
        if directory in self._loaded:
            return
        rules: list[str] = []
        if self.use_gitignore:
            rules.extend(self._read_rules(directory / ".gitignore"))
        if self.use_ssxignore:
            rules.extend(self._read_rules(directory / ".ssxignore"))
        if rules:
            self._specs[directory] = pathspec.PathSpec.from_lines("gitignore", rules)
        self._loaded.add(directory)
        self._cache.clear()

    def _relative(self, path: Path, base: Path | None = None) -> str:
        relative = path.resolve().relative_to(base or self.root).as_posix()
        return f"{relative}/" if path.is_dir() and not relative.endswith("/") else relative

    def ignored(self, path: Path) -> bool:
        """Return whether a path is ignored by the effective rule stack."""

        resolved = path.resolve()
        cached = self._cache.get(resolved)
        if cached is not None:
            return cached
        relative = self._relative(resolved)
        ignored = self.base_spec.match_file(relative)
        ancestors = [
            directory
            for directory in reversed(resolved.parents)
            if directory == self.root or self.root in directory.parents
        ]
        for directory in ancestors:
            spec = self._specs.get(directory)
            if spec is not None:
                decision = spec.check_file(self._relative(resolved, directory))
                if decision.include is not None:
                    ignored = decision.include
        if self.include_spec and not resolved.is_dir():
            ignored = ignored or not self.include_spec.match_file(relative)
        if len(self._cache) >= 131_072:
            self._cache.clear()
        self._cache[resolved] = ignored
        return ignored

    def prune(self, directory: Path, names: list[str]) -> int:
        """Prune ignored child directories in-place and return the count."""

        kept: list[str] = []
        for name in names:
            child = directory / name
            if not self.ignored(child):
                kept.append(name)
        removed = len(names) - len(kept)
        names[:] = kept
        return removed

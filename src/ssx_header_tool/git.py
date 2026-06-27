"""Small, typed Git command adapter."""

from __future__ import annotations

import subprocess
from pathlib import Path

from .exceptions import GitError


def _run(root: Path, *arguments: str) -> str:
    try:
        process = subprocess.run(
            ["git", "-C", str(root), *arguments],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", "") or str(exc)
        raise GitError(detail.strip()) from exc
    return process.stdout


def _paths(root: Path, *arguments: str) -> list[Path]:
    output = _run(root, *arguments, "-z")
    return [(root / name).resolve() for name in output.split("\0") if name]


def tracked(root: Path) -> list[Path]:
    """Return files tracked by Git."""

    return _paths(root.resolve(), "ls-files")


def modified(root: Path) -> list[Path]:
    """Return unstaged modified and untracked files."""

    root = root.resolve()
    changed = _paths(root, "diff", "--name-only")
    untracked = _paths(root, "ls-files", "--others", "--exclude-standard")
    return list(dict.fromkeys([*changed, *untracked]))


def staged(root: Path) -> list[Path]:
    """Return files staged in the index."""

    return _paths(root.resolve(), "diff", "--cached", "--name-only")


def branch(root: Path) -> str:
    """Return the current branch name."""

    return _run(root.resolve(), "branch", "--show-current").strip()


def status(root: Path) -> str:
    """Return porcelain repository status."""

    return _run(root.resolve(), "status", "--short")

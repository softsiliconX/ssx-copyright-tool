"""Small path utilities."""

from pathlib import Path


def normalize(path: str | Path) -> Path:
    """Return an absolute normalized path."""

    return Path(path).resolve()

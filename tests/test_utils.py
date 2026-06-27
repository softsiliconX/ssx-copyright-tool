"""Utility tests."""

from pathlib import Path

from ssx_header_tool.utils import normalize


def test_normalize(tmp_path: Path) -> None:
    assert normalize(tmp_path / "..") == tmp_path.parent.resolve()

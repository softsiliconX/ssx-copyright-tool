# Copyright (c) 2026 SoftSiliconX Pvt Ltd
# All rights reserved.
#
# File Name        : test_git.py
# File Description :
# Author           : Santhosh
# Date             : 2026-06-28

"""Git adapter integration tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from ssx_header_tool.exceptions import GitError
from ssx_header_tool.git import branch, modified, staged, status, tracked


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-b", "main", str(tmp_path)], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "config", "user.email", "test@example.com"],
        check=True,
    )
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "Test"], check=True)
    path = tmp_path / "a.py"
    path.write_text("pass\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "a.py"], check=True)
    subprocess.run(
        ["git", "-C", str(tmp_path), "commit", "-m", "initial"],
        check=True,
        capture_output=True,
    )
    return tmp_path


def test_tracked(repository: Path) -> None:
    assert [path.name for path in tracked(repository)] == ["a.py"]


def test_modified(repository: Path) -> None:
    (repository / "a.py").write_text("print('changed')\n", encoding="utf-8")
    (repository / "new.py").touch()
    assert {path.name for path in modified(repository)} == {"a.py", "new.py"}


def test_staged(repository: Path) -> None:
    (repository / "a.py").write_text("print('changed')\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repository), "add", "a.py"], check=True)
    assert [path.name for path in staged(repository)] == ["a.py"]


def test_branch(repository: Path) -> None:
    assert branch(repository) == "main"


def test_status(repository: Path) -> None:
    (repository / "new.py").touch()
    assert "new.py" in status(repository)


def test_not_repository(tmp_path: Path) -> None:
    with pytest.raises(GitError):
        tracked(tmp_path)

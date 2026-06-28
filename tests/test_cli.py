# Copyright (c) 2026 SoftSiliconX Pvt Ltd
# All rights reserved.
#
# File Name        : test_cli.py
# File Description :
# Author           : Santhosh
# Date             : 2026-06-28

"""CLI tests."""

from __future__ import annotations

from pathlib import Path

from ssx_header_tool import cli
from ssx_header_tool.cli import build_parser, main
from ssx_header_tool.models import Config


def test_parser_commands() -> None:
    parser = build_parser()
    for command in ("add", "update", "remove", "verify", "preview", "report"):
        assert parser.parse_args([command]).command == command


def test_init(tmp_path: Path) -> None:
    assert main(["init", str(tmp_path)]) == 0
    assert (tmp_path / "ssxconfig.yaml").is_file()


def test_add_verify_remove(tmp_path: Path) -> None:
    path = tmp_path / "a.py"
    path.write_text("pass\n", encoding="utf-8")
    assert main(["add", str(path), "--report", "json"]) == 0
    assert main(["verify", str(path), "--report", "json"]) == 0
    assert main(["remove", str(path), "--report", "json"]) == 0
    assert main(["verify", str(path), "--report", "json"]) == 1


def test_preview_no_write(tmp_path: Path) -> None:
    path = tmp_path / "a.py"
    path.write_text("pass\n", encoding="utf-8")
    assert main(["preview", str(path), "--report", "json"]) == 0
    assert path.read_text(encoding="utf-8") == "pass\n"


def test_config_command(tmp_path: Path) -> None:
    assert main(["config", str(tmp_path)]) == 0


def test_bad_config(tmp_path: Path) -> None:
    (tmp_path / "ssxconfig.yaml").write_text("year: bad\n", encoding="utf-8")
    assert main(["add", str(tmp_path)]) == 2


def test_directory_scan(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("pass\n", encoding="utf-8")
    assert main(["add", str(tmp_path), "--report", "json"]) == 0


def test_git_selection_helpers(tmp_path: Path, monkeypatch: object) -> None:
    path = tmp_path / "a.py"
    path.touch()
    for option, name in (("--git", "tracked"), ("--modified", "modified"), ("--staged", "staged")):
        arguments = build_parser().parse_args(["verify", str(tmp_path), option])
        monkeypatch.setattr(cli, name, lambda _root, selected=path: [selected])
        files, ignored = cli._files(arguments, Config(root=tmp_path, year=2026))
        assert files == [path] and ignored == 0

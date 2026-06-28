# Copyright (c) 2026 SoftSiliconX Pvt Ltd
# All rights reserved.
#
# File Name        : test_processor.py
# File Description :
# Author           : Santhosh
# Date             : 2026-06-28

"""Processor behavior and preservation tests."""

from __future__ import annotations

import codecs
import os
from dataclasses import replace
from pathlib import Path

import pytest

from ssx_header_tool.models import Config, Operation, ResultStatus
from ssx_header_tool.processor import Processor


@pytest.mark.parametrize(
    "filename",
    ["a.py", "a.c", "a.cpp", "a.java", "a.go", "a.rs", "a.sh", "a.sql",
     "a.xml", "a.html", "a.css", "a.js", "a.ts", "Dockerfile", "a.yaml",
     "a.toml", "a.ini", "a.properties", "a.lua", "Makefile", "CMakeLists.txt"],
)
def test_add_supported_styles(tmp_path: Path, config: Config, filename: str) -> None:
    path = tmp_path / filename
    path.write_text("content\n", encoding="utf-8")
    result = Processor(config).process(path, Operation.ADD)
    assert result.status == ResultStatus.ADDED
    assert "Example Corp" in path.read_text(encoding="utf-8")


def test_add_skip_existing(tmp_path: Path, config: Config) -> None:
    path = tmp_path / "a.py"
    path.write_text("print('ok')\n", encoding="utf-8")
    processor = Processor(config)
    assert processor.process(path, "add").status == ResultStatus.ADDED
    assert processor.process(path, "add").status == ResultStatus.SKIPPED


def test_update(tmp_path: Path, config: Config) -> None:
    path = tmp_path / "a.py"
    path.write_text("print('ok')\n", encoding="utf-8")
    Processor(config).process(path, "add")
    updated = replace(config, company="New Corp")
    result = Processor(updated).update(path)
    assert result.status == ResultStatus.UPDATED
    assert "New Corp" in path.read_text(encoding="utf-8")


def test_remove(tmp_path: Path, config: Config) -> None:
    path = tmp_path / "a.py"
    original = "print('ok')\n"
    path.write_text(original, encoding="utf-8")
    processor = Processor(config)
    processor.process(path, "add")
    assert processor.remove(path).status == ResultStatus.REMOVED
    assert path.read_text(encoding="utf-8") == original


def test_verify_missing_and_valid(tmp_path: Path, config: Config) -> None:
    path = tmp_path / "a.py"
    path.write_text("pass\n", encoding="utf-8")
    processor = Processor(config)
    assert processor.verify(path).status == ResultStatus.MISSING
    processor.process(path, "add")
    assert processor.verify(path).status == ResultStatus.VALID


def test_preview_does_not_write(tmp_path: Path, config: Config) -> None:
    path = tmp_path / "a.py"
    original = "pass\n"
    path.write_text(original, encoding="utf-8")
    result = Processor(config).preview(path)
    assert result.changed and result.diff.startswith("---")
    assert path.read_text(encoding="utf-8") == original


def test_dry_run_does_not_write(tmp_path: Path, config: Config) -> None:
    path = tmp_path / "a.py"
    path.write_text("pass\n", encoding="utf-8")
    result = Processor(config).process(path, "add", dry_run=True)
    assert result.status == ResultStatus.ADDED
    assert path.read_text(encoding="utf-8") == "pass\n"


@pytest.mark.parametrize("newline", ["\n", "\r\n"])
def test_preserves_newline(tmp_path: Path, config: Config, newline: str) -> None:
    path = tmp_path / "a.py"
    path.write_bytes(f"one{newline}two{newline}".encode())
    Processor(config).process(path, "add")
    raw = path.read_bytes()
    if newline == "\r\n":
        assert b"\r\n" in raw and raw.replace(b"\r\n", b"").find(b"\n") < 0
    else:
        assert b"\r\n" not in raw


@pytest.mark.parametrize(
    ("bom", "encoding"),
    [
        (codecs.BOM_UTF8, "utf-8"),
        (codecs.BOM_UTF16_LE, "utf-16-le"),
        (codecs.BOM_UTF16_BE, "utf-16-be"),
        (codecs.BOM_UTF32_LE, "utf-32-le"),
        (codecs.BOM_UTF32_BE, "utf-32-be"),
    ],
)
def test_preserves_bom(
    tmp_path: Path, config: Config, bom: bytes, encoding: str
) -> None:
    path = tmp_path / "a.py"
    path.write_bytes(bom + "pass\n".encode(encoding))
    Processor(config).process(path, "add")
    assert path.read_bytes().startswith(bom)


@pytest.mark.parametrize(
    ("filename", "preamble"),
    [
        ("a.py", "#!/usr/bin/env python\n"),
        ("a.sh", "#!/bin/sh\n"),
        ("a.xml", "<?xml version=\"1.0\"?>\n"),
        ("a.php", "<?php\n"),
    ],
)
def test_preserves_preamble(
    tmp_path: Path, config: Config, filename: str, preamble: str
) -> None:
    path = tmp_path / filename
    path.write_text(preamble + "content\n", encoding="utf-8")
    Processor(config).process(path, "add")
    assert path.read_text(encoding="utf-8").startswith(preamble)


def test_preserves_permissions(tmp_path: Path, config: Config) -> None:
    path = tmp_path / "a.py"
    path.write_text("pass\n", encoding="utf-8")
    os.chmod(path, 0o744)
    before = path.stat().st_mode
    Processor(config).process(path, "add")
    assert path.stat().st_mode == before


def test_preserves_timestamp(tmp_path: Path, config: Config) -> None:
    path = tmp_path / "a.py"
    path.write_text("pass\n", encoding="utf-8")
    os.utime(path, ns=(1_700_000_000_000_000_000, 1_700_000_000_000_000_000))
    before = path.stat().st_mtime_ns
    Processor(config).process(path, "add")
    assert path.stat().st_mtime_ns == before


def test_unsupported_file(tmp_path: Path, config: Config) -> None:
    path = tmp_path / "a.bin"
    path.write_bytes(b"content")
    result = Processor(config).process(path, "add")
    assert result.status == ResultStatus.ERROR


def test_backward_compatible_add(tmp_path: Path, config: Config) -> None:
    path = tmp_path / "a.py"
    path.write_text("pass\n", encoding="utf-8")
    assert Processor(config).add(path, "Linus") == "added"
    assert "Linus" in path.read_text(encoding="utf-8")


def test_latin1_fallback(tmp_path: Path, config: Config) -> None:
    path = tmp_path / "a.py"
    path.write_bytes("caf\xe9\n".encode("latin-1"))
    assert Processor(config).process(path, "add").status == ResultStatus.ADDED
    assert b"caf\xe9" in path.read_bytes()


def test_has_header(tmp_path: Path, config: Config) -> None:
    path = tmp_path / "a.py"
    path.write_text("pass\n", encoding="utf-8")
    processor = Processor(config)
    assert not processor.has_header(path)
    processor.process(path, "add")
    assert processor.has_header(path)


@pytest.mark.parametrize("operation", ["update", "remove"])
def test_missing_header_skips(
    tmp_path: Path, config: Config, operation: str
) -> None:
    path = tmp_path / "a.py"
    path.write_text("pass\n", encoding="utf-8")
    assert Processor(config).process(path, operation).status == ResultStatus.SKIPPED


def test_preview_existing_header(tmp_path: Path, config: Config) -> None:
    path = tmp_path / "a.py"
    path.write_text("pass\n", encoding="utf-8")
    processor = Processor(config)
    processor.process(path, "add")
    result = Processor(replace(config, company="Changed")).preview(path)
    assert result.status == ResultStatus.UPDATED
    assert "Changed" in result.diff


def test_timestamp_can_change(tmp_path: Path, config: Config) -> None:
    path = tmp_path / "a.py"
    path.write_text("pass\n", encoding="utf-8")
    old = 1_600_000_000_000_000_000
    os.utime(path, ns=(old, old))
    Processor(replace(config, preserve_timestamps=False)).process(path, "add")
    assert path.stat().st_mtime_ns != old


def test_shebang_without_newline(tmp_path: Path, config: Config) -> None:
    path = tmp_path / "a.py"
    path.write_text("#!/usr/bin/python", encoding="utf-8")
    Processor(config).process(path, "add")
    assert path.read_text(encoding="utf-8").startswith("#!/usr/bin/python")


@pytest.mark.parametrize(
    ("filename", "content"),
    [
        ("a.c", "Copyright All rights reserved.\n"),
        ("a.c", "/* Copyright All rights reserved.\n"),
        ("a.py", "Copyright All rights reserved.\n"),
    ],
)
def test_malformed_header_is_not_managed(
    tmp_path: Path, config: Config, filename: str, content: str
) -> None:
    path = tmp_path / filename
    path.write_text(content, encoding="utf-8")
    assert not Processor(config).has_header(path)

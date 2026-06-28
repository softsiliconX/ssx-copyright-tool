# Copyright (c) 2026 SoftSiliconX Pvt Ltd
# All rights reserved.
#
# File Name        : processor.py
# File Description :
# Author           : Santhosh
# Date             : 2026-06-28

"""Safe source header processing.

Encoding, newline, parsing, and atomic writing are intentionally private to
this module so all transformations share one preservation contract.
"""

from __future__ import annotations

import codecs
import difflib
import os
import stat
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .comments import comment_style, render
from .constants import HEADER_MARKERS
from .exceptions import ProcessingError
from .models import Config, Operation, ProcessResult, ResultStatus
from .templates import TemplateLoader


@dataclass(slots=True)
class _Document:
    text: str
    encoding: str
    bom: bytes
    newline: str
    mode: int
    atime_ns: int
    mtime_ns: int


_BOMS = (
    (codecs.BOM_UTF32_LE, "utf-32-le"),
    (codecs.BOM_UTF32_BE, "utf-32-be"),
    (codecs.BOM_UTF8, "utf-8"),
    (codecs.BOM_UTF16_LE, "utf-16-le"),
    (codecs.BOM_UTF16_BE, "utf-16-be"),
)


def _read_document(path: Path) -> _Document:
    raw = path.read_bytes()
    encoding = "utf-8"
    bom = b""
    payload = raw
    for signature, candidate in _BOMS:
        if raw.startswith(signature):
            bom, encoding, payload = signature, candidate, raw[len(signature):]
            break
    try:
        text = payload.decode(encoding)
    except UnicodeDecodeError:
        try:
            encoding = "utf-8"
            text = raw.decode(encoding)
        except UnicodeDecodeError:
            encoding = "latin-1"
            text = raw.decode(encoding)
        bom = b""
    newline = "\r\n" if b"\r\n" in raw else "\n"
    info = path.stat()
    return _Document(
        text=text,
        encoding=encoding,
        bom=bom,
        newline=newline,
        mode=stat.S_IMODE(info.st_mode),
        atime_ns=info.st_atime_ns,
        mtime_ns=info.st_mtime_ns,
    )


def _encode(document: _Document, text: str) -> bytes:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return document.bom + normalized.replace("\n", document.newline).encode(document.encoding)


def _atomic_write(path: Path, data: bytes, document: _Document, preserve_times: bool) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, document.mode)
        os.replace(temporary, path)
        if preserve_times:
            os.utime(path, ns=(document.atime_ns, document.mtime_ns))
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def _preamble_end(text: str, path: Path) -> int:
    position = 0
    lower_name = path.name.lower()
    if text.startswith("#!"):
        newline = text.find("\n")
        position = len(text) if newline < 0 else newline + 1
    remainder = text[position:]
    if remainder.startswith("<?xml"):
        end = remainder.find("?>")
        if end >= 0:
            position += end + 2
            while text[position:position + 1] in {"\r", "\n"}:
                position += 1
    elif lower_name.endswith(".php") and remainder.startswith("<?php"):
        end = remainder.find("\n")
        position += len(remainder) if end < 0 else end + 1
    return position


def _header_range(text: str, path: Path) -> tuple[int, int] | None:
    start = _preamble_end(text, path)
    probe = text[start:start + 8192]
    if not all(marker in probe[:4096] for marker in HEADER_MARKERS):
        return None
    style = comment_style(path)
    if style is None:
        return None
    if style in {"cblock", "xml"}:
        opening, closing = ("/*", "*/") if style == "cblock" else ("<!--", "-->")
        if not probe.lstrip().startswith(opening):
            return None
        leading = len(probe) - len(probe.lstrip())
        end = probe.find(closing, leading)
        if end < 0:
            return None
        end += len(closing)
    else:
        prefix = {"sql": "--", "ini": ";"}.get(style, "#")
        offset = 0
        lines = probe.splitlines(keepends=True)
        matched = False
        for line in lines:
            if line.strip() and not line.lstrip().startswith(prefix):
                break
            matched = matched or any(marker in line for marker in HEADER_MARKERS)
            offset += len(line)
        if not matched:
            return None
        end = offset
    while end < len(probe) and probe[end] in "\r\n":
        end += 1
    return start, start + end


class Processor:
    """Add, update, remove, verify, and preview source headers."""

    def __init__(
        self,
        config: Config | None = None,
        template_loader: TemplateLoader | None = None,
    ) -> None:
        self.config = config or Config(year=date.today().year)
        self.template_loader = template_loader or TemplateLoader(self.config.template_dir)
        self.template = self.template_loader.load(self.config.template)
        self.template_loader.validate(self.template)

    def build_header(self, path: Path, author: str | None = None) -> str:
        """Build a rendered header for one source path."""

        style = comment_style(path)
        if style is None:
            raise ProcessingError(f"Unsupported source type: {path}")
        today = date.today()
        body = self.template_loader.render(
            self.template,
            {
                "company": self.config.company,
                "author": self.config.author if author is None else author,
                "filename": path.name,
                "year": self.config.year or today.year,
                "date": today.isoformat(),
                "description": self.config.description,
            },
        )
        return render(style, tuple(body.splitlines()))

    def has_header(self, path: Path) -> bool:
        """Return whether a recognized managed header exists."""

        document = _read_document(path)
        return _header_range(document.text, path) is not None

    def process(
        self,
        path: Path,
        operation: Operation | str,
        *,
        dry_run: bool = False,
    ) -> ProcessResult:
        """Apply one operation to a source file."""

        path = path.resolve()
        selected = Operation(operation)
        try:
            document = _read_document(path)
            existing = _header_range(document.text, path)
            if selected == Operation.VERIFY:
                status = ResultStatus.VALID if existing else ResultStatus.MISSING
                return ProcessResult(path, status)

            header = self.build_header(path)
            insertion = _preamble_end(document.text, path)
            if selected == Operation.ADD:
                if existing:
                    return ProcessResult(path, ResultStatus.SKIPPED)
                new_text = document.text[:insertion] + header + "\n\n" + document.text[insertion:]
                status = ResultStatus.ADDED
            elif selected == Operation.UPDATE:
                if not existing:
                    return ProcessResult(path, ResultStatus.SKIPPED)
                new_text = (
                    document.text[: existing[0]]
                    + header
                    + "\n\n"
                    + document.text[existing[1] :]
                )
                status = ResultStatus.UPDATED
            elif selected == Operation.REMOVE:
                if not existing:
                    return ProcessResult(path, ResultStatus.SKIPPED)
                new_text = document.text[:existing[0]] + document.text[existing[1]:]
                status = ResultStatus.REMOVED
            elif selected == Operation.PREVIEW:
                if existing:
                    new_text = (
                        document.text[: existing[0]]
                        + header
                        + "\n\n"
                        + document.text[existing[1] :]
                    )
                    status = ResultStatus.UPDATED
                else:
                    new_text = (
                        document.text[:insertion]
                        + header
                        + "\n\n"
                        + document.text[insertion:]
                    )
                    status = ResultStatus.ADDED
            else:
                raise ProcessingError(f"Unsupported operation: {selected}")

            if new_text == document.text:
                return ProcessResult(path, ResultStatus.SKIPPED)
            diff = "".join(
                difflib.unified_diff(
                    document.text.splitlines(keepends=True),
                    new_text.splitlines(keepends=True),
                    fromfile=str(path),
                    tofile=str(path),
                )
            )
            if not dry_run and selected != Operation.PREVIEW:
                _atomic_write(
                    path,
                    _encode(document, new_text),
                    document,
                    self.config.preserve_timestamps,
                )
            return ProcessResult(path, status, changed=True, diff=diff)
        except (OSError, UnicodeError, ProcessingError) as exc:
            return ProcessResult(path, ResultStatus.ERROR, error=str(exc))

    def add(self, path: Path, author: str | None = None, dry_run: bool = False) -> str:
        """Backward-compatible add operation returning a status string."""

        original_author = self.config.author
        if author is not None:
            self.config.author = author
        try:
            return self.process(path, Operation.ADD, dry_run=dry_run).status.value
        finally:
            self.config.author = original_author

    def update(self, path: Path, dry_run: bool = False) -> ProcessResult:
        """Update an existing managed header."""

        return self.process(path, Operation.UPDATE, dry_run=dry_run)

    def remove(self, path: Path, dry_run: bool = False) -> ProcessResult:
        """Remove an existing managed header."""

        return self.process(path, Operation.REMOVE, dry_run=dry_run)

    def verify(self, path: Path) -> ProcessResult:
        """Verify that a managed header exists."""

        return self.process(path, Operation.VERIFY)

    def preview(self, path: Path) -> ProcessResult:
        """Preview the add or update diff without writing."""

        return self.process(path, Operation.PREVIEW, dry_run=True)

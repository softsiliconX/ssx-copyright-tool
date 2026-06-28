# Copyright (c) 2026 SoftSiliconX Pvt Ltd
# All rights reserved.
#
# File Name        : comments.py
# File Description :
# Author           : Santhosh
# Date             : 2026-06-28

"""Comment style detection and rendering."""

from __future__ import annotations

from pathlib import Path

from .constants import STYLE_BY_EXTENSION, STYLE_BY_NAME


def comment_style(path: str | Path) -> str | None:
    """Return the header comment style for a path."""

    candidate = Path(path)
    return STYLE_BY_NAME.get(
        candidate.name.lower(), STYLE_BY_EXTENSION.get(candidate.suffix.lower())
    )


def render(style: str, lines: list[str] | tuple[str, ...]) -> str:
    """Render plain header lines in a supported comment style."""

    if style == "cblock":
        return "\n".join(["/*", *(f" * {line}" if line else " *" for line in lines), " */"])
    if style == "xml":
        return "\n".join(["<!--", *lines, "-->"])
    prefix = {"sql": "--", "ini": ";"}.get(style, "#")
    return "\n".join(f"{prefix} {line}".rstrip() for line in lines)


def delimiters(style: str) -> tuple[str, str]:
    """Return first and last header delimiter prefixes."""

    if style == "cblock":
        return "/*", "*/"
    if style == "xml":
        return "<!--", "-->"
    prefix = {"sql": "--", "ini": ";"}.get(style, "#")
    return prefix, prefix

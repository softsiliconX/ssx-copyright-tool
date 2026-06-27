"""Comment engine tests."""

from __future__ import annotations

import pytest

from ssx_header_tool.comments import comment_style, delimiters, render


@pytest.mark.parametrize(
    ("filename", "style"),
    [
        ("a.py", "hash"), ("a.pyi", "hash"), ("a.sh", "hash"), ("a.yaml", "hash"),
        ("a.yml", "hash"), ("a.toml", "hash"), ("Dockerfile", "hash"),
        ("Makefile", "hash"), ("CMakeLists.txt", "hash"), ("a.cmake", "hash"),
        ("a.c", "cblock"), ("a.h", "cblock"), ("a.cc", "cblock"),
        ("a.cpp", "cblock"), ("a.hpp", "cblock"), ("a.java", "cblock"),
        ("a.go", "cblock"), ("a.rs", "cblock"), ("a.js", "cblock"),
        ("a.jsx", "cblock"), ("a.ts", "cblock"), ("a.tsx", "cblock"),
        ("a.css", "cblock"), ("a.php", "cblock"), ("a.xml", "xml"),
        ("a.html", "xml"), ("a.htm", "xml"), ("a.sql", "sql"),
        ("a.ini", "ini"), ("a.cfg", "ini"), ("a.properties", "hash"),
        ("a.lua", "sql"),
    ],
)
def test_comment_style(filename: str, style: str) -> None:
    assert comment_style(filename) == style


@pytest.mark.parametrize(
    ("style", "expected"),
    [
        ("hash", "# one\n#\n# two"),
        ("sql", "-- one\n--\n-- two"),
        ("ini", "; one\n;\n; two"),
        ("cblock", "/*\n * one\n *\n * two\n */"),
        ("xml", "<!--\none\n\ntwo\n-->"),
    ],
)
def test_render(style: str, expected: str) -> None:
    assert render(style, ("one", "", "two")) == expected


@pytest.mark.parametrize(
    ("style", "expected"),
    [
        ("hash", ("#", "#")),
        ("sql", ("--", "--")),
        ("ini", (";", ";")),
        ("cblock", ("/*", "*/")),
        ("xml", ("<!--", "-->")),
    ],
)
def test_delimiters(style: str, expected: tuple[str, str]) -> None:
    assert delimiters(style) == expected


def test_unknown_extension() -> None:
    assert comment_style("file.bin") is None

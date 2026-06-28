# Copyright (c) 2026 SoftSiliconX Pvt Ltd
# All rights reserved.
#
# File Name        : test_templates.py
# File Description :
# Author           : Santhosh
# Date             : 2026-06-28

"""Template tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from ssx_header_tool.exceptions import ConfigurationError
from ssx_header_tool.templates import TemplateLoader


def test_default_template() -> None:
    assert "{company}" in TemplateLoader().load()


def test_default_template_from_directory(tmp_path: Path) -> None:
    (tmp_path / "default.txt").write_text("local {company}", encoding="utf-8")
    assert TemplateLoader(tmp_path).load() == "local {company}"


def test_named_template(tmp_path: Path) -> None:
    (tmp_path / "short.txt").write_text("{year} {company}", encoding="utf-8")
    assert TemplateLoader(tmp_path).load("short") == "{year} {company}"


def test_explicit_template(tmp_path: Path) -> None:
    path = tmp_path / "custom.header"
    path.write_text("{author}", encoding="utf-8")
    assert TemplateLoader().load(str(path)) == "{author}"


def test_missing_template(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError):
        TemplateLoader(tmp_path).load("missing")


@pytest.mark.parametrize(
    "placeholder", ["company", "author", "filename", "year", "date", "description"]
)
def test_valid_placeholders(placeholder: str) -> None:
    TemplateLoader().validate("{" + placeholder + "}")


def test_unknown_placeholder() -> None:
    with pytest.raises(ConfigurationError):
        TemplateLoader().validate("{license}")


def test_render() -> None:
    assert TemplateLoader().render(
        "{company}/{year}", {"company": "ACME", "year": 2026}
    ) == "ACME/2026"


def test_render_missing_value() -> None:
    with pytest.raises(ConfigurationError):
        TemplateLoader().render("{company}/{year}", {"company": "ACME"})

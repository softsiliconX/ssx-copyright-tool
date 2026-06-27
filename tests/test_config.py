"""Configuration tests."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
import yaml

from ssx_header_tool.config import load_config, write_default_config
from ssx_header_tool.exceptions import ConfigurationError


def test_defaults(tmp_path: Path) -> None:
    config = load_config(root=tmp_path, environ={})
    assert config.year == date.today().year
    assert config.root == tmp_path.resolve()


def test_yaml_values(tmp_path: Path) -> None:
    path = tmp_path / "custom.yaml"
    path.write_text("company: ACME\nauthor: Grace\nyear: 2020\n", encoding="utf-8")
    config = load_config(path, root=tmp_path, environ={})
    assert (config.company, config.author, config.year) == ("ACME", "Grace", 2020)


def test_precedence(tmp_path: Path) -> None:
    path = tmp_path / "ssxconfig.yaml"
    path.write_text("company: YAML\n", encoding="utf-8")
    config = load_config(
        path,
        root=tmp_path,
        environ={"SSX_HEADER_COMPANY": "ENV"},
        overrides={"company": "CLI"},
    )
    assert config.company == "CLI"


@pytest.mark.parametrize("value", ["true", "1", "yes", "on", True])
def test_true_values(tmp_path: Path, value: object) -> None:
    config = load_config(
        root=tmp_path, overrides={"use_gitignore": value}, environ={}
    )
    assert config.use_gitignore is True


@pytest.mark.parametrize("value", ["false", "0", "no", "off", False])
def test_false_values(tmp_path: Path, value: object) -> None:
    config = load_config(
        root=tmp_path, overrides={"use_gitignore": value}, environ={}
    )
    assert config.use_gitignore is False


@pytest.mark.parametrize("value", [0, 10000, "bad"])
def test_invalid_year(tmp_path: Path, value: object) -> None:
    with pytest.raises(ConfigurationError):
        load_config(root=tmp_path, overrides={"year": value}, environ={})


@pytest.mark.parametrize("value", ["xml", "pdf", "text"])
def test_invalid_report(tmp_path: Path, value: str) -> None:
    with pytest.raises(ConfigurationError):
        load_config(root=tmp_path, overrides={"report": value}, environ={})


def test_unknown_key(tmp_path: Path) -> None:
    path = tmp_path / "ssxconfig.yaml"
    path.write_text("mystery: true\n", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_config(path, root=tmp_path, environ={})


def test_non_mapping_yaml(tmp_path: Path) -> None:
    path = tmp_path / "ssxconfig.yaml"
    path.write_text("- item\n", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_config(path, root=tmp_path, environ={})


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("py, js", ("py", "js")),
        (["py", "js"], ("py", "js")),
        ((), ()),
        (None, ()),
    ],
)
def test_sequence_values(tmp_path: Path, value: object, expected: tuple[str, ...]) -> None:
    config = load_config(root=tmp_path, overrides={"extensions": value}, environ={})
    assert config.extensions == expected


def test_write_default(tmp_path: Path) -> None:
    destination = write_default_config(tmp_path / "ssxconfig.yaml")
    assert yaml.safe_load(destination.read_text(encoding="utf-8"))["report"] == "console"


def test_write_default_refuses_overwrite(tmp_path: Path) -> None:
    destination = tmp_path / "ssxconfig.yaml"
    destination.write_text("company: Existing\n", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        write_default_config(destination)


def test_invalid_boolean(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError):
        load_config(root=tmp_path, overrides={"use_gitignore": "maybe"}, environ={})


def test_invalid_sequence(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError):
        load_config(root=tmp_path, overrides={"extensions": 42}, environ={})


def test_invalid_yaml(tmp_path: Path) -> None:
    path = tmp_path / "ssxconfig.yaml"
    path.write_text("company: [\n", encoding="utf-8")
    with pytest.raises(ConfigurationError):
        load_config(path, root=tmp_path, environ={})

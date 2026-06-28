# Copyright (c) 2026 SoftSiliconX Pvt Ltd
# All rights reserved.
#
# File Name        : config.py
# File Description :
# Author           : Santhosh
# Date             : 2026-06-28

"""Configuration loading, validation, and initialization."""

from __future__ import annotations

import os
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from .constants import CONFIG_FILENAME, DEFAULT_COMPANY
from .exceptions import ConfigurationError
from .models import Config

ENV_PREFIX = "SSX_HEADER_"
_FIELDS = {
    "company", "author", "year", "description", "template", "template_dir",
    "use_gitignore", "use_ssxignore", "include", "exclude", "extensions",
    "preserve_timestamps", "report",
}


def _boolean(value: Any, name: str) -> bool:
    if isinstance(value, bool):
        return value
    normalized = str(value).strip().lower()
    if normalized in {"1", "true", "yes", "on"}:
        return True
    if normalized in {"0", "false", "no", "off"}:
        return False
    raise ConfigurationError(f"{name} must be a boolean")


def _sequence(value: Any, name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return tuple(part.strip() for part in value.split(",") if part.strip())
    if isinstance(value, list | tuple) and all(isinstance(item, str) for item in value):
        return tuple(value)
    raise ConfigurationError(f"{name} must be a string or list of strings")


def _environment(environ: Mapping[str, str]) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for field in _FIELDS:
        key = f"{ENV_PREFIX}{field.upper()}"
        if key in environ:
            values[field] = environ[key]
    return values


def load_config(
    path: str | Path | None = None,
    *,
    root: str | Path | None = None,
    overrides: Mapping[str, Any] | None = None,
    environ: Mapping[str, str] | None = None,
) -> Config:
    """Load config with precedence defaults, YAML, environment, then CLI."""

    resolved_root = Path(root or Path.cwd()).resolve()
    config_path = Path(path).resolve() if path else resolved_root / CONFIG_FILENAME
    data: dict[str, Any] = {}
    if config_path.exists():
        try:
            loaded = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
        except (OSError, yaml.YAMLError) as exc:
            raise ConfigurationError(f"Cannot read {config_path}: {exc}") from exc
        if not isinstance(loaded, dict):
            raise ConfigurationError("Configuration root must be a mapping")
        unknown = set(loaded) - _FIELDS
        if unknown:
            raise ConfigurationError(f"Unknown configuration keys: {', '.join(sorted(unknown))}")
        data.update(loaded)
    data.update(_environment(environ or os.environ))
    data.update({key: value for key, value in (overrides or {}).items() if value is not None})

    try:
        year = int(data.get("year", date.today().year))
    except (TypeError, ValueError) as exc:
        raise ConfigurationError("year must be an integer") from exc
    if not 1 <= year <= 9999:
        raise ConfigurationError("year must be between 1 and 9999")
    report = str(data.get("report", "console")).lower()
    if report not in {"console", "json", "csv", "html", "markdown"}:
        raise ConfigurationError(f"Unsupported report format: {report}")

    template_dir = data.get("template_dir")
    return Config(
        root=resolved_root,
        company=str(data.get("company", DEFAULT_COMPANY)).strip(),
        author=str(data.get("author", "")).strip(),
        year=year,
        description=str(data.get("description", "")),
        template=str(data.get("template", "default")),
        template_dir=Path(template_dir) if template_dir else None,
        use_gitignore=_boolean(data.get("use_gitignore", True), "use_gitignore"),
        use_ssxignore=_boolean(data.get("use_ssxignore", True), "use_ssxignore"),
        include=_sequence(data.get("include"), "include"),
        exclude=_sequence(data.get("exclude"), "exclude"),
        extensions=_sequence(data.get("extensions"), "extensions"),
        preserve_timestamps=_boolean(
            data.get("preserve_timestamps", True), "preserve_timestamps"
        ),
        report=report,
    )


def write_default_config(path: str | Path, *, force: bool = False) -> Path:
    """Create a documented default YAML configuration."""

    destination = Path(path)
    if destination.exists() and not force:
        raise ConfigurationError(f"Configuration already exists: {destination}")
    content = {
        "company": DEFAULT_COMPANY,
        "author": "",
        "year": date.today().year,
        "template": "default",
        "use_gitignore": True,
        "use_ssxignore": True,
        "preserve_timestamps": True,
        "report": "console",
    }
    destination.write_text(yaml.safe_dump(content, sort_keys=False), encoding="utf-8")
    return destination

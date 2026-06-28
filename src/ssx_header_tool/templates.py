# Copyright (c) 2026 SoftSiliconX Pvt Ltd
# All rights reserved.
#
# File Name        : templates.py
# File Description :
# Author           : Santhosh
# Date             : 2026-06-28

"""Header template loading and rendering."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from string import Formatter

from .constants import DEFAULT_TEMPLATE
from .exceptions import ConfigurationError

PLACEHOLDERS = {"company", "author", "filename", "year", "date", "description"}


class TemplateLoader:
    """Load templates from a repository-level template directory."""

    def __init__(self, template_dir: Path | None = None) -> None:
        self.template_dir = template_dir

    def load(self, name_or_path: str = "default") -> str:
        """Load a named or explicitly addressed template."""

        if name_or_path == "default":
            if self.template_dir:
                candidate = self.template_dir / "default.txt"
                if candidate.is_file():
                    return candidate.read_text(encoding="utf-8")
            return DEFAULT_TEMPLATE
        explicit = Path(name_or_path)
        candidates = [explicit]
        if self.template_dir:
            candidates.extend(
                [self.template_dir / name_or_path, self.template_dir / f"{name_or_path}.txt"]
            )
        for candidate in candidates:
            if candidate.is_file():
                return candidate.read_text(encoding="utf-8")
        raise ConfigurationError(f"Template not found: {name_or_path}")

    def validate(self, template: str) -> None:
        """Validate placeholders before processing any files."""

        fields = {name for _, name, _, _ in Formatter().parse(template) if name}
        unknown = fields - PLACEHOLDERS
        if unknown:
            raise ConfigurationError(f"Unknown template placeholders: {', '.join(sorted(unknown))}")

    def render(self, template: str, values: Mapping[str, object]) -> str:
        """Render a validated template."""

        self.validate(template)
        missing = PLACEHOLDERS.intersection(
            name for _, name, _, _ in Formatter().parse(template) if name
        ) - values.keys()
        if missing:
            raise ConfigurationError(f"Missing template values: {', '.join(sorted(missing))}")
        return template.format_map(values)

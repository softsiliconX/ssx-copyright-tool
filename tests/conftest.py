# Copyright (c) 2026 SoftSiliconX Pvt Ltd
# All rights reserved.
#
# File Name        : conftest.py
# File Description :
# Author           : Santhosh
# Date             : 2026-06-28

"""Shared test fixtures."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from ssx_header_tool.models import Config


@pytest.fixture
def config(tmp_path: Path) -> Config:
    """Return a deterministic test configuration."""

    return Config(
        root=tmp_path,
        company="Example Corp",
        author="Ada",
        year=date.today().year,
        description="Test file",
        preserve_timestamps=True,
    )

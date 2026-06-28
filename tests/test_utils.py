# Copyright (c) 2026 SoftSiliconX Pvt Ltd
# All rights reserved.
#
# File Name        : test_utils.py
# File Description :
# Author           : Santhosh
# Date             : 2026-06-28

"""Utility tests."""

from pathlib import Path

from ssx_header_tool.utils import normalize


def test_normalize(tmp_path: Path) -> None:
    assert normalize(tmp_path / "..") == tmp_path.parent.resolve()

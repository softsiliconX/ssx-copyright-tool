# Copyright (c) 2026 SoftSiliconX Pvt Ltd
# All rights reserved.
#
# File Name        : utils.py
# File Description :
# Author           : Santhosh
# Date             : 2026-06-28

"""Small path utilities."""

from pathlib import Path


def normalize(path: str | Path) -> Path:
    """Return an absolute normalized path."""

    return Path(path).resolve()

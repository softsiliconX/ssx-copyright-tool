# Copyright (c) 2026 SoftSiliconX Pvt Ltd
# All rights reserved.
#
# File Name        : test_import.py
# File Description :
# Author           : Santhosh
# Date             : 2026-06-28

from ssx_header_tool.version import __version__


def test_version():
    assert __version__ == "2.0.0"

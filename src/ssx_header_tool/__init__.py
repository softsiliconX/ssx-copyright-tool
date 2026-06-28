# Copyright (c) 2026 SoftSiliconX Pvt Ltd
# All rights reserved.
#
# File Name        : __init__.py
# File Description :
# Author           : Santhosh
# Date             : 2026-06-28

"""SSX Header Tool public package API."""

from .models import Config, Operation, ProcessResult, ResultStatus
from .processor import Processor
from .scanner import RepositoryScanner
from .version import __version__

__all__ = [
    "Config",
    "Operation",
    "ProcessResult",
    "Processor",
    "RepositoryScanner",
    "ResultStatus",
    "__version__",
]

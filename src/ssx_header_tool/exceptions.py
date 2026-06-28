# Copyright (c) 2026 SoftSiliconX Pvt Ltd
# All rights reserved.
#
# File Name        : exceptions.py
# File Description :
# Author           : Santhosh
# Date             : 2026-06-28

"""Package exceptions."""


class SSXHeaderError(Exception):
    """Base package error."""


class ConfigurationError(SSXHeaderError):
    """Configuration is missing or invalid."""


class ProcessingError(SSXHeaderError):
    """A source file cannot be processed safely."""


class GitError(SSXHeaderError):
    """A Git command failed."""

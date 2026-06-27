"""Package exceptions."""


class SSXHeaderError(Exception):
    """Base package error."""


class ConfigurationError(SSXHeaderError):
    """Configuration is missing or invalid."""


class ProcessingError(SSXHeaderError):
    """A source file cannot be processed safely."""


class GitError(SSXHeaderError):
    """A Git command failed."""

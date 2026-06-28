# Copyright (c) 2026 SoftSiliconX Pvt Ltd
# All rights reserved.
#
# File Name        : constants.py
# File Description :
# Author           : Santhosh
# Date             : 2026-06-28

"""Application constants."""

TOOL_NAME = "SSX Header Tool"
CONFIG_FILENAME = "ssxconfig.yaml"
DEFAULT_COMPANY = "SoftSiliconX Pvt Ltd"
DEFAULT_AUTHOR = ""
DEFAULT_TEMPLATE = """Copyright (c) {year} {company}
All rights reserved.

File Name        : {filename}
File Description : {description}
Author           : {author}
Date             : {date}"""

DEFAULT_IGNORES = (
    ".git/",
    ".hg/",
    ".svn/",
    ".idea/",
    ".vscode/",
    ".mypy_cache/",
    ".pytest_cache/",
    ".ruff_cache/",
    ".next/",
    "node_modules/",
    "dist/",
    "build/",
    "coverage/",
    "target/",
    "__pycache__/",
    "venv/",
    ".venv/",
)

STYLE_BY_EXTENSION = {
    ".py": "hash", ".pyi": "hash", ".c": "cblock", ".h": "cblock",
    ".cc": "cblock", ".cpp": "cblock", ".cxx": "cblock", ".hh": "cblock",
    ".hpp": "cblock", ".java": "cblock", ".go": "cblock", ".rs": "cblock",
    ".js": "cblock", ".jsx": "cblock", ".ts": "cblock", ".tsx": "cblock",
    ".css": "cblock", ".scss": "cblock", ".sh": "hash", ".bash": "hash",
    ".zsh": "hash", ".yaml": "hash", ".yml": "hash", ".toml": "hash",
    ".xml": "xml", ".html": "xml", ".htm": "xml", ".sql": "sql",
    ".ini": "ini", ".cfg": "ini", ".properties": "hash", ".lua": "sql",
    ".cmake": "hash", ".php": "cblock",
}

STYLE_BY_NAME = {
    "dockerfile": "hash",
    "makefile": "hash",
    "gnumakefile": "hash",
    "cmakelists.txt": "hash",
}

HEADER_MARKERS = ("Copyright", "All rights reserved.")

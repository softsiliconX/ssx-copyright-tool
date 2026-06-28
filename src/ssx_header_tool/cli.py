# Copyright (c) 2026 SoftSiliconX Pvt Ltd
# All rights reserved.
#
# File Name        : cli.py
# File Description :
# Author           : Santhosh
# Date             : 2026-06-28

"""Command-line interface."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path
from typing import Any

from rich.console import Console

from .config import load_config, write_default_config
from .constants import CONFIG_FILENAME
from .exceptions import SSXHeaderError
from .git import modified, staged, tracked
from .ignore import IgnoreEngine
from .models import Config, Operation, ProcessResult
from .processor import Processor
from .report import ReportWriter, Summary
from .scanner import RepositoryScanner
from .version import __version__


def _add_common_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("path", nargs="?", default=".", help="Repository or source file")
    parser.add_argument("--config", dest="config_path", help="Configuration file")
    parser.add_argument("--author")
    parser.add_argument("--company")
    parser.add_argument("--year", type=int)
    parser.add_argument("--template")
    parser.add_argument("--dry-run", action="store_true")
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--git", action="store_true", help="Process tracked files")
    selection.add_argument("--modified", action="store_true", help="Process modified files")
    selection.add_argument("--staged", action="store_true", help="Process staged files")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--report",
        choices=("console", "json", "csv", "html", "markdown"),
        help="Report format",
    )
    parser.add_argument("--report-file", type=Path)


def build_parser() -> argparse.ArgumentParser:
    """Build the public argument parser."""

    parser = argparse.ArgumentParser(prog="ssx-header", description="Manage source code headers")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    for command in ("add", "update", "remove", "verify", "preview", "report"):
        child = commands.add_parser(command)
        _add_common_options(child)
    initialize = commands.add_parser("init")
    initialize.add_argument("path", nargs="?", default=".")
    initialize.add_argument("--force", action="store_true")
    show_config = commands.add_parser("config")
    show_config.add_argument("path", nargs="?", default=".")
    show_config.add_argument("--config", dest="config_path")
    return parser


def _overrides(arguments: argparse.Namespace) -> dict[str, Any]:
    return {
        "author": getattr(arguments, "author", None),
        "company": getattr(arguments, "company", None),
        "year": getattr(arguments, "year", None),
        "template": getattr(arguments, "template", None),
        "report": getattr(arguments, "report", None),
    }


def _selected_paths(arguments: argparse.Namespace, root: Path) -> list[Path] | None:
    if arguments.git:
        return tracked(root)
    if arguments.modified:
        return modified(root)
    if arguments.staged:
        return staged(root)
    return None


def _files(arguments: argparse.Namespace, config: Config) -> tuple[list[Path], int]:
    target = Path(arguments.path).resolve()
    if target.is_file():
        return [target], 0
    selected = _selected_paths(arguments, target)
    if selected is not None:
        return [path for path in selected if path.is_file()], 0
    engine = IgnoreEngine(
        target,
        use_gitignore=config.use_gitignore,
        use_ssxignore=config.use_ssxignore,
        include=config.include,
        exclude=config.exclude,
    )
    scanner = RepositoryScanner(target, ignore_engine=engine, extensions=config.extensions)
    files = [entry.path for entry in scanner.scan()]
    return files, scanner.statistics.ignored


def _execute(arguments: argparse.Namespace) -> int:
    target = Path(arguments.path).resolve()
    root = target if target.is_dir() else target.parent
    config = load_config(
        arguments.config_path,
        root=root,
        overrides=_overrides(arguments),
    )
    processor = Processor(config)
    files, ignored = _files(arguments, config)
    command = Operation.VERIFY if arguments.command == "report" else Operation(arguments.command)
    results: list[ProcessResult] = []
    summary = Summary(scanned=len(files), ignored=ignored)
    console = Console(stderr=True)
    for path in files:
        result = processor.process(path, command, dry_run=arguments.dry_run)
        results.append(result)
        summary.record(result)
        if arguments.verbose or arguments.command == "preview":
            console.print(f"{result.status.value:8} {path}")
        if result.diff and arguments.command == "preview":
            console.print(result.diff, markup=False, highlight=False)
    format_name = arguments.report or config.report
    ReportWriter().write(format_name, summary, results, arguments.report_file)
    if summary.errors:
        return 2
    if command == Operation.VERIFY and summary.missing:
        return 1
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line application."""

    parser = build_parser()
    arguments = parser.parse_args(argv)
    try:
        if arguments.command == "init":
            destination = Path(arguments.path).resolve() / CONFIG_FILENAME
            write_default_config(destination, force=arguments.force)
            Console().print(f"Created {destination}")
            return 0
        if arguments.command == "config":
            root = Path(arguments.path).resolve()
            config = load_config(arguments.config_path, root=root)
            payload = {
                key: str(value) if isinstance(value, Path) else value
                for key, value in asdict(config).items()
            }
            Console().print_json(json.dumps(payload))
            return 0
        return _execute(arguments)
    except (SSXHeaderError, OSError, ValueError) as exc:
        Console(stderr=True).print(f"[red]error:[/red] {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())

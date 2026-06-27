"""Report tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from rich.console import Console

from ssx_header_tool.models import ProcessResult, ResultStatus
from ssx_header_tool.report import ReportWriter, Summary


@pytest.mark.parametrize(
    ("status", "field"),
    [
        (ResultStatus.ADDED, "added"),
        (ResultStatus.UPDATED, "updated"),
        (ResultStatus.REMOVED, "removed"),
        (ResultStatus.SKIPPED, "skipped"),
        (ResultStatus.ERROR, "errors"),
        (ResultStatus.VALID, "valid"),
        (ResultStatus.MISSING, "missing"),
    ],
)
def test_summary_record(status: ResultStatus, field: str, tmp_path: Path) -> None:
    summary = Summary()
    summary.record(ProcessResult(tmp_path / "a.py", status))
    assert getattr(summary, field) == 1


@pytest.mark.parametrize("format_name", ["json", "csv", "html", "markdown"])
def test_report_formats(format_name: str, tmp_path: Path) -> None:
    result = ProcessResult(tmp_path / "a.py", ResultStatus.ADDED, changed=True)
    output = ReportWriter().write(format_name, Summary(scanned=1, added=1), [result])
    assert "a.py" in output


def test_json_structure(tmp_path: Path) -> None:
    output = ReportWriter().write("json", Summary(scanned=2), [])
    assert json.loads(output)["statistics"]["scanned"] == 2


def test_report_destination(tmp_path: Path) -> None:
    destination = tmp_path / "report.md"
    ReportWriter().write("markdown", Summary(), [], destination)
    assert destination.read_text(encoding="utf-8").startswith("# SSX")


def test_invalid_report() -> None:
    with pytest.raises(ValueError):
        ReportWriter().write("pdf", Summary(), [])


def test_summary_print(tmp_path: Path) -> None:
    destination = tmp_path / "console.txt"
    with destination.open("w", encoding="utf-8") as stream:
        Summary(scanned=1).print(Console(file=stream, force_terminal=False))
    assert "Scanned" in destination.read_text(encoding="utf-8")


def test_summary_save_json(tmp_path: Path) -> None:
    destination = tmp_path / "summary.json"
    result = ProcessResult(tmp_path / "a.py", ResultStatus.VALID)
    Summary(scanned=1, valid=1).save_json(destination, [result])
    assert json.loads(destination.read_text(encoding="utf-8"))["files"][0]["status"] == "valid"


def test_console_report() -> None:
    assert ReportWriter().write("console", Summary(), []) == ""

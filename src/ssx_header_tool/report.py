# Copyright (c) 2026 SoftSiliconX Pvt Ltd
# All rights reserved.
#
# File Name        : report.py
# File Description :
# Author           : Santhosh
# Date             : 2026-06-28

"""Operation summaries and report serializers."""

from __future__ import annotations

import csv
import html
import json
from dataclasses import asdict, dataclass
from io import StringIO
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .models import ProcessResult, ResultStatus


@dataclass(slots=True)
class Summary:
    """Aggregate operation statistics."""

    scanned: int = 0
    added: int = 0
    updated: int = 0
    removed: int = 0
    skipped: int = 0
    ignored: int = 0
    errors: int = 0
    valid: int = 0
    missing: int = 0

    def record(self, result: ProcessResult) -> None:
        """Record one process result."""

        mapping = {
            ResultStatus.ADDED: "added",
            ResultStatus.UPDATED: "updated",
            ResultStatus.REMOVED: "removed",
            ResultStatus.SKIPPED: "skipped",
            ResultStatus.ERROR: "errors",
            ResultStatus.VALID: "valid",
            ResultStatus.MISSING: "missing",
        }
        field = mapping[result.status]
        setattr(self, field, getattr(self, field) + 1)

    def as_dict(self) -> dict[str, int]:
        """Return statistics as a dictionary."""

        return asdict(self)

    def print(self, console: Console | None = None) -> None:
        """Print a Rich console table."""

        table = Table(title="SSX Header Summary")
        table.add_column("Metric")
        table.add_column("Count", justify="right")
        for key, value in self.as_dict().items():
            table.add_row(key.title(), str(value))
        (console or Console()).print(table)

    def save_json(self, path: Path, results: list[ProcessResult] | None = None) -> None:
        """Write a JSON report."""

        payload = {
            "statistics": self.as_dict(),
            "files": [item.as_dict() for item in results or []],
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


class ReportWriter:
    """Write summaries in console, JSON, CSV, HTML, or Markdown."""

    def write(
        self,
        format_name: str,
        summary: Summary,
        results: list[ProcessResult],
        destination: Path | None = None,
    ) -> str:
        """Serialize and optionally save a report."""

        selected = format_name.lower()
        if selected == "console":
            summary.print()
            return ""
        if selected == "json":
            output = json.dumps(
                {"statistics": summary.as_dict(), "files": [item.as_dict() for item in results]},
                indent=2,
            )
        elif selected == "csv":
            stream = StringIO()
            writer = csv.DictWriter(
                stream, fieldnames=["path", "status", "changed", "diff", "error"]
            )
            writer.writeheader()
            writer.writerows(item.as_dict() for item in results)
            output = stream.getvalue()
        elif selected == "markdown":
            rows = ["| Path | Status | Changed | Error |", "|---|---|---:|---|"]
            rows.extend(
                f"| {item.path} | {item.status.value} | {item.changed} | {item.error} |"
                for item in results
            )
            output = "\n".join(
                [
                    "# SSX Header Report",
                    "",
                    *[f"- {key}: {value}" for key, value in summary.as_dict().items()],
                    "",
                    *rows,
                ]
            )
        elif selected == "html":
            stats = "".join(
                f"<li><strong>{html.escape(key)}</strong>: {value}</li>"
                for key, value in summary.as_dict().items()
            )
            html_rows = "".join(
                "<tr>"
                f"<td>{html.escape(str(item.path))}</td>"
                f"<td>{html.escape(item.status.value)}</td>"
                f"<td>{str(item.changed).lower()}</td>"
                f"<td>{html.escape(item.error)}</td>"
                "</tr>"
                for item in results
            )
            output = (
                "<!doctype html><html><head><meta charset=\"utf-8\">"
                "<title>SSX Header Report</title></head><body>"
                f"<h1>SSX Header Report</h1><ul>{stats}</ul>"
                "<table><thead><tr><th>Path</th><th>Status</th><th>Changed</th>"
                f"<th>Error</th></tr></thead><tbody>{html_rows}</tbody></table></body></html>"
            )
        else:
            raise ValueError(f"Unsupported report format: {selected}")
        if destination:
            destination.write_text(output, encoding="utf-8", newline="")
        return output

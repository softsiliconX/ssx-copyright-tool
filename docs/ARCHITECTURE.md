# Architecture

## Layers

`cli.py` resolves arguments and configuration, selects scanner or Git inputs,
dispatches operations, and chooses a report writer.

`config.py` merges defaults, `ssxconfig.yaml`, `SSX_HEADER_*` environment
variables, and CLI overrides. Validation occurs before traversal.

`ignore.py` compiles Git-ignore-compatible rules with `pathspec`. Rules are
cached by directory, nested ignore files are loaded while walking, and ignored
directories are pruned before descent.

`scanner.py` is a lazy, read-only `os.walk` scanner. It filters supported source
types, detects binaries and symlinks, records statistics, and supports progress
callbacks.

`processor.py` owns the complete transformation contract. Private document I/O
preserves BOM, encoding, LF/CRLF, permissions, timestamps, shebangs, XML
declarations, and PHP opening tags.

`comments.py`, `templates.py`, `git.py`, and `report.py` provide language
rendering, validated substitution, repository selection, and output adapters.

## Processing Flow

1. Resolve and validate configuration.
2. Select files from the scanner or Git.
3. Read each file and capture preservation metadata.
4. Locate its protected preamble and managed header.
5. Compute the operation and unified diff.
6. Atomically replace changed files unless preview or dry-run is active.
7. Aggregate and emit statistics.

The scanner never writes and the processor never traverses, keeping large
repository behavior predictable and mutation independently testable.

# SSX Header Tool

SSX Header Tool is a Python 3.11+ utility for adding, updating, removing,
verifying, and reporting source-code headers across large repositories. It
preserves encodings, BOMs, line endings, preambles, permissions, and timestamps.

## Install

```console
python -m pip install .
```

For development:

```console
python -m pip install -e ".[dev]"
```

## Quick Start

```console
ssx-header init .
ssx-header preview .
ssx-header add .
ssx-header verify .
```

The same interface is available through `python -m ssx_header_tool`.

## Run Against Another Repository

Install the tool from this directory first:

```console
python -m pip install -e .
```

Then add copyright headers to a neighboring repository and set the author:

```console
ssx-header add ..\ssx-nexux\ --author "Santhosh"
```

You can also run it through Python without using the installed command:

```console
python -m ssx_header_tool add ..\ssx-nexux\ --author "Santhosh"
```

This replaces the old script-style invocation:

```console
python .\ssx_copyright_tool.py ..\ssx-nexux\ --author "Santhosh"
```

Use `preview` in place of `add` to inspect the changes before writing files.

### Ignore Generated Prisma Migrations

Do not add or update headers in existing Prisma migration files. Changing an
applied migration can alter its checksum and cause migration drift. Add a
`.ssxignore` file at the root of the target repository containing:

```gitignore
apps/api/prisma/migrations/
```

If the header tool already changed those files, review the diff and restore
them before running the tool again:

```console
git diff -- apps/api/prisma/migrations
git restore -- apps/api/prisma/migrations
```

## Commands

- `add`: add headers only where missing
- `update`: replace recognized headers
- `remove`: remove recognized headers
- `verify`: return exit code 1 when headers are missing
- `preview`: print unified diffs without writing
- `report`: emit console, JSON, CSV, HTML, or Markdown output
- `init`: create `ssxconfig.yaml`
- `config`: print the resolved configuration

Detailed references are in [CLI](docs/CLI.md),
[architecture](docs/ARCHITECTURE.md), and
[template format](docs/TemplateFormat.md).

## Development

```console
ruff check src tests
mypy src
pytest --cov=ssx_header_tool --cov-report=term-missing
python -m build
```

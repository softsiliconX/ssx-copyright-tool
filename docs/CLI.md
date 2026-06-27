# CLI Reference

```console
ssx-header COMMAND [PATH] [OPTIONS]
```

`PATH` defaults to the current directory and may be a repository or one file.

Common options:

- `--author`, `--company`, `--year`: override template values
- `--template`: named template or template file
- `--dry-run`: compute changes without writing
- `--git`, `--modified`, `--staged`: select files through Git
- `--verbose`: print every outcome
- `--report`: `console`, `json`, `csv`, `html`, or `markdown`
- `--report-file`: write the report to a file
- `--config`: use a specific YAML configuration

Exit codes are 0 for success, 1 for missing headers during verification, and 2
for configuration, Git, or processing errors.

```console
ssx-header add src --author "Ada Lovelace"
ssx-header update . --modified
ssx-header preview service.py
ssx-header verify . --git
ssx-header report . --report json --report-file headers.json
```

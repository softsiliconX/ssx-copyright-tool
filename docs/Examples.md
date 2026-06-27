# Examples

## Configuration

```yaml
company: Example Corp
author: Platform Engineering
year: 2026
description: Internal source file
template: default
use_gitignore: true
use_ssxignore: true
preserve_timestamps: true
include:
  - "src/**"
exclude:
  - "src/generated/**"
report: console
```

## Ignore Rules

```gitignore
vendor/
*.generated.py
```

Nested `.gitignore` and `.ssxignore` files are applied relative to their own
directories.

## CI Verification

```console
ssx-header verify . --git --report json --report-file header-report.json
```

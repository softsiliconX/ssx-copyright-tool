# Template Format

Templates are UTF-8 plain text without comment delimiters. Supported
placeholders are `{company}`, `{author}`, `{filename}`, `{year}`, `{date}`, and
`{description}`.

```text
Copyright (c) {year} {company}
All rights reserved.

File Name        : {filename}
File Description : {description}
Author           : {author}
Date             : {date}
```

Unknown placeholders and missing values fail before files are processed. A
custom template can be selected by name from `template_dir` or by direct path.

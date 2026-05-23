# source_code/

Bundled configuration assets for bash_common commands. Not source code in the
typical sense — the directory name is historical.

## Contents

| File | Used by | Purpose |
|------|---------|---------|
| `allman.uncrust.cfg` | `uncrust`, `files format-cpp` | Allman-style Uncrustify configuration applied when reformatting C/C++ source files. |

## Adding new assets

This directory is the right home for any read-only resource that ships with
bash_common and is consumed by a command at runtime — code-style configs,
templates, sample data, and similar fixtures. Keep filenames descriptive and
update the table above so the directory remains self-documenting.

Per-command code lives at the bash_common root; per-language reusable Python
code lives in `lib/`. This directory is intentionally separate from both.

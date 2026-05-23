BASH_COMMON DESIGN
==================

This document describes how bash_common is intended to scale as a portable
command system. The README is the user-facing command reference; this file is
for design, architecture, and implementation direction.

## Direction

bash_common is moving toward a modular command model:

```text
command subcommand [options] [args]
```

`video` is the first command that follows this pattern. Existing standalone
commands should continue to work, but future work should gradually group related
tools into command families with subcommands.

Examples:

```text
video info FILE
video thumb FILE

project new-git
project new-unity
project new-shell

files rename
files format-cpp

android install
android run
android log
```

The command line remains first-class. Any web UI or automation layer must wrap
the same commands rather than replacing them.

## Repository Layout

The repository is intentionally flat. Commands live at the root because they
need to be on `PATH`; everything else lives in a small set of well-known
directories.

| Path | Purpose |
|------|---------|
| `*` (root, executable) | First-class commands, one per file. Metadata-backed where applicable. |
| `commands/` | Bash-side init: aliases, colour helpers, bookmarks, config helpers loaded by `.bashrc`. |
| `darwin/`, `cygwin/`, `unix/` | Platform-specific commands and `_init.sh`. Selected from `uname -s` at startup. |
| `lib/` | Shared Python helpers consumed by commands and the UI (`bc_config`, `bc_metadata`, `bc_group`, `bc_output`). |
| `webui/` | Flask app served by `bcui`. Reads command metadata via `lib/bc_metadata`. |
| `completion/` | Bash completion scripts. `bash_common.completion.bash` is the metadata-driven generic completer; the others are vendored from upstream tools. |
| `source_code/` | Bundled read-only configuration assets shipped with commands (e.g. `allman.uncrust.cfg`). Despite the name, this is not source code. See its README for details. |
| `tests/` | `unittest` suite covering metadata discovery, shell startup, and `bcui`. |

## Shared Python Library

Python commands should share reusable project functionality through `lib/`.
Command files should stay focused on their command-specific behaviour and
metadata rather than accumulating repeated plumbing.

Current shared modules:

```text
lib/
  bc_config.py     .bcconfig discovery, loading, provenance, path abbreviation
  bc_group.py      thin wrappers for grouped commands that delegate to old tools
  bc_metadata.py   command metadata discovery, command environment, config defaults
  bc_output.py     terminal output cleanup helpers
```

Use `lib/` for code that is needed by more than one command or by both a command
and `bcui`. Good candidates include:

- `.bcconfig` traversal and merging.
- Command metadata discovery and validation helpers.
- Artifact path handling.
- Subprocess/job helpers.
- Common output formatting.
- Small platform-detection utilities.

Avoid moving command-specific business logic into `lib/` too early. For example,
video probing, encoding decisions, and ffmpeg command construction should remain
owned by `video` until another command genuinely needs the same behaviour.

## Grouped Commands

All grouped commands are first-class Python commands following the same
architecture: inline argparse handlers, `bc_metadata()` for discovery, and
`.bcconfig` integration for user-configurable defaults.

| Group | Subcommands | Config section |
|-------|-------------|----------------|
| `bashcommon` | `init`, `update`, `config`, `ui`, `doctor`, `list` | — |
| `project` | `git-init`, `unity-init`, `shell-script`, `cmake`, `cmake-dir` | — |
| `files` | `rename`, `format-cpp` | `[files]` |
| `android` | `install`, `uninstall`, `run`, `log`, `list`, `dump`, `activity`, `devices`, `adb`, `config` | `[android]` |
| `blender` | `launch`, `python`, `config` | `[blender]` |
| `docs` | `cheat`, `markdown` | `[docs]` |
| `safari` | `cookies` | `[safari]` |

## BC UI

`bcui` is the local web UI command. It starts a Flask server bound
to localhost and provides an interactive browser interface for supported
bash_common commands.

Default behaviour:

```bash
bcui
```

```text
BC UI running at http://127.0.0.1:8765
Press Ctrl-C to stop.
```

Useful flags:

```text
bcui --host 127.0.0.1
bcui --port 8765
bcui --cwd /path/to/project
bcui --no-browser
bcui --host 0.0.0.0 --allow-lan
```

Non-localhost binds require `--allow-lan` because the UI is a local command
runner. It should only be exposed on a trusted network.

The UI should support:

- Browsing available command groups and subcommands.
- Running structured command forms.
- Typing a supported command line.
- Starting commands as background jobs.
- Polling live stdout, stderr, exit code, runtime, and job status.
- Cancelling running jobs.
- Viewing generated artifacts such as images, HTML reports, JSON, and logs.
- Showing the effective `.bcconfig` for the selected working directory.

## No Central Registry

The UI and other tools must not rely on a hard-coded central registry of
commands. Command metadata belongs with the command itself.

The scalable model is:

1. Discovery scans bash_common command locations.
2. Each command can expose metadata through a standard machine-readable entry
   point.
3. Tools such as `bcui` and `bcconfig` read that metadata directly from the
   command.
4. Adding or changing a command does not require updating a central registry.

Shared discovery mechanics live in `lib/bc_metadata.py`; the metadata itself
still belongs to each command.

Discovery has two modes:

- normal discovery, which returns valid commands for tools such as `bcui`;
- diagnostic discovery, which also returns invalid metadata, failed commands,
  and timeouts for `bashcommon doctor`.

## Completion

Bash completion is metadata-backed. `completion/bash_common.completion.bash`
registers executable bash_common commands that advertise `--bc-metadata`, then
uses that metadata to complete:

- subcommand names,
- declared long and short options,
- choice values,
- path-like arguments.

This keeps completion aligned with the same command metadata used by `bcui` and
`bcconfig`. Grouped passthrough commands complete their subcommands and then
fall back to path completion for delegated arguments until those subcommands are
rewritten with richer argument metadata.

Completion caches each command's metadata by executable modification time. This
keeps tab completion fast while still allowing command edits to invalidate the
cache naturally.

Recommended metadata entry point:

```bash
command --bc-metadata
```

The output should be JSON. It should be fast, side-effect free, and valid even
when optional runtime dependencies such as `ffmpeg`, `adb`, or `uncrustify` are
not installed.

## Command Metadata

Each command owns its metadata. Metadata can describe:

- Command name and summary.
- Subcommands.
- Arguments and options.
- UI field hints.
- Config defaults and `.bcconfig` sections.
- Generated artifact types.
- Safety level.
- Dependency checks.

Example shape:

```json
{
  "schema_version": 1,
  "name": "video",
  "summary": "ffmpeg-backed video tools",
  "command_style": "subcommands",
  "config_sections": {
    "video": [
      {
        "key": "default_format",
        "default": "mp4",
        "description": "Default container format"
      }
    ],
    "video.thumb": [
      {
        "key": "time",
        "default": "00:00:01",
        "description": "Default timestamp for frame extraction"
      }
    ]
  },
  "subcommands": [
    {
      "name": "info",
      "summary": "Print detailed file and stream information",
      "args": [
        {
          "name": "file",
          "kind": "path",
          "required": true,
          "exists": true
        }
      ],
      "options": [
        {
          "name": "json",
          "flag": "--json",
          "kind": "boolean"
        }
      ],
      "artifacts": [
        {
          "kind": "json",
          "source": "stdout",
          "when": "--json"
        }
      ]
    },
    {
      "name": "thumb",
      "summary": "Extract a single frame as a PNG image",
      "args": [
        {
          "name": "file",
          "kind": "path",
          "required": true,
          "exists": true
        }
      ],
      "options": [
        {
          "name": "time",
          "flag": "-t",
          "kind": "string",
          "config": "video.thumb.time"
        },
        {
          "name": "output",
          "flag": "-o",
          "kind": "path",
          "artifact": "image/png"
        }
      ],
      "artifacts": [
        {
          "kind": "image",
          "path_option": "output"
        }
      ]
    }
  ]
}
```

The exact schema can evolve, but it should remain command-owned and
machine-readable.

## Config Integration

`.bcconfig` remains the shared configuration system for both CLI and UI usage.

Current behaviour:

- `.bcconfig` files are discovered from the user's home directory down to the
  current working directory.
- More local files override parent settings.
- `bcconfig` displays effective settings and provenance.
- Commands can read values through `bc_cfg_get` or their own config loader.

Target behaviour:

- `bcconfig` discovers config schemas from command metadata.
- Commands should expose their config defaults in `--bc-metadata`.
- `bcconfig --init` should generate templates from all discovered command
  metadata rather than from hard-coded knowledge.
- `bcui` should pre-fill form defaults from the effective `.bcconfig`.
- Project-local `.bcconfig` files should affect CLI and UI command runs in the
  same way.

## Discovery

Discovery should prefer explicit bash_common locations over arbitrary system
paths:

```text
$BC_INSTALL_DIR
$BC_INSTALL_DIR/$BC_SYSTEM
```

A discovered executable is considered a bash_common command if it successfully
responds to:

```bash
command --bc-metadata
```

Legacy commands without metadata can still exist and remain callable from the
shell. They should not appear as rich UI commands until they implement metadata.

## Execution Model

`bcui` should execute commands as structured argument vectors, not shell
strings.

Good:

```python
subprocess.Popen([
    str(command_path),
    "thumb",
    "-t", timestamp,
    "-o", output_path,
    input_path,
])
```

Avoid:

```python
subprocess.Popen(
    f"video thumb -t {timestamp} -o {output_path} {input_path}",
    shell=True,
)
```

Rules:

- Bind the server to `127.0.0.1` by default.
- Do not provide an arbitrary shell prompt in the browser.
- Parse typed commands with `shlex`.
- Accept only discovered commands and metadata-declared subcommands/options.
- Show the exact command before running destructive operations.
- Capture stdout, stderr, exit code, duration, cwd, and artifacts.

## Jobs And Artifacts

Every UI command run should be represented as a job:

```text
job id
command argv
working directory
start/end time
stdout
stderr
exit code
artifacts
```

Artifact handling examples:

| Command | Artifact |
|---------|----------|
| `video info --json FILE` | JSON rendered in the UI. |
| `video thumb -o thumb.png FILE` | PNG preview. |
| `video catalog -o report.html DIR` | HTML report link or preview. |
| `video normalise -n DIR` | Dry-run HTML report. |

Initial job history can be in-memory. Persistent history can be added later if
it proves useful.

## Migration Plan

1. Add metadata support to `video`. Done.
2. Add shared Python helpers in `lib/`. Done.
3. Add `bcui` with Flask, command discovery, config display, and job execution. Done.
4. Build generated UI forms for metadata-backed commands. Done.
5. Add typed command input limited to discovered metadata. Done.
6. Update `bcconfig` to consume command metadata for config defaults. Done.
7. Add grouped command entry points for standalone commands. Done.
8. Rewrite grouped commands as first-class Python commands with inline logic,
   real argparse, `bc_metadata()`, and `.bcconfig` integration. Done.
   Legacy standalone scripts removed; the grouped commands are the sole entry
   points.

## Testing Direction

The repo has a focused `unittest` suite under `tests/`. As metadata and UI
behaviour are added, tests should cover:

- Metadata JSON validity.
- Command discovery.
- `.bcconfig` schema generation from metadata.
- Structured argv construction.
- Rejection of unsupported typed commands.
- Artifact detection.
- Flask endpoint smoke tests.
- Quiet shell startup in noninteractive shells.

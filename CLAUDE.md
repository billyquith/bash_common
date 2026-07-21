# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

`bash_common` is a portable Bash environment plus a set of first-class commands,
biased toward game development. It targets macOS (`darwin`), Cygwin/Windows
(`cygwin`), and other UNIX-like systems (`unix`). The user-facing command
reference is `README.md`; architecture and design direction live in `design.md`.

## Commands

```bash
# Run the test suite (must run from the repo root so `from lib import ...` resolves)
python3 -m unittest discover -s tests

# Run a single test module / class / method
python3 -m unittest tests.test_metadata
python3 -m unittest tests.test_metadata.MetadataTests.test_android_subcommands

# Validate that every metadata-backed command publishes valid metadata
bashcommon doctor          # add --json for machine-readable output

# List discovered commands; --markdown regenerates the README command table
bashcommon list --with-subcommands

# Install/repair dependencies, the local .venv, shell config, and completions
bcinit

# Inspect a command's machine-readable metadata directly
./video --bc-metadata
```

Python dependencies (`Flask`, `markdown2`) live in a repo-local `.venv` created
by `bcinit`, not a system install. `ffmpeg`/`ffprobe` (video) and `adb`
(android) are optional runtime deps — commands and their `--bc-metadata` must
still work when these are absent.

## Architecture

### Two layers: shell init vs. commands

1. **Shell init** — `.profile` (login shell: sets `BC_INSTALL_DIR`, adds it to
   `PATH`) and `.bashrc` (interactive shell: sets `BC_SYSTEM`/`BC_OS` from
   `uname -s`, sources everything in `commands/`, loads platform `_init.sh` and
   completions). `BC_QUIET=1` suppresses the welcome banner. Non-interactive
   shells return early from `.bashrc` before any output — keep it that way
   (`tests/test_shell_startup.py` enforces quiet noninteractive startup).
2. **Commands** — executables at the repo root, one per file, on `PATH`. Each is
   either a first-class Python command or a vendored helper.

The repository layout is intentionally flat because commands must be on `PATH`.
Platform-specific commands and `_init.sh` live in `darwin/`, `cygwin/`, `unix/`,
selected at startup from `uname -s` (see `system_dir()` in `lib/bc_metadata.py`).

### Command model: metadata-driven, no central registry

This is the core architectural idea — read `design.md` before changing it.
There is **no hard-coded list of commands** anywhere. Instead:

- Each grouped command is a Python executable following the same shape (see
  `blender`, `bashcommon`, `android`, etc.): a `bc_metadata()` function returning
  a dict, a `main(argv)` that prints `json.dumps(bc_metadata())` when called with
  exactly `--bc-metadata`, and an argparse-based subcommand dispatcher.
- `lib/bc_metadata.py` discovers commands by scanning the root + platform dir,
  filtering to executables that contain a `--bc-metadata` marker, running each
  with `--bc-metadata`, and parsing the JSON. Discovery has a **normal** mode
  (valid commands, used by `bcui`/completion) and a **diagnostic** mode
  (`inspect_commands`, also returns failures/timeouts, used by `bashcommon doctor`).
- `bcui`, completion (`completion/bash_common.completion.bash`), and `bcconfig`
  all consume this metadata. **Adding or changing a command must not require
  editing a registry** — put the change in the command's own metadata.

Consequence: when you add a subcommand, option, or config key to a command, the
canonical source of truth is its `bc_metadata()` output. Completion, the UI, and
config templates derive from it automatically. `tests/test_metadata.py` asserts
the exact subcommand and config-key sets per group, so update both together.

### Shared library (`lib/`)

Reusable plumbing only — command-specific business logic (e.g. ffmpeg
construction in `video`) stays in the command until a second consumer needs it.

- `bc_config.py` — `.bcconfig` discovery, merging, and provenance.
- `bc_metadata.py` — command discovery, command env, config defaults from metadata.
- `bc_group.py` — helpers for grouped commands.
- `bc_output.py` — terminal output cleanup.

### Configuration: `.bcconfig`

Hierarchical INI-style config discovered from `~` down to the current directory
(`bc_config.find_files`); **more local files override parents**. Commands read
values via this loader (or the `bc_cfg_get` shell helper); section names match
the command (`[android]`, `[video]`, `[blender]`, ...). `bcconfig` shows
effective values and provenance. `android` also reads legacy `~/.uadb` /
`./.uadb` `KEY=VALUE` files for backward compatibility, overridden by `.bcconfig`.

### Web UI (`bcui` / `webui/`)

Flask app that runs discovered commands as **structured argv vectors, never
shell strings** (parse typed input with `shlex`; accept only discovered
commands and metadata-declared subcommands/options). Binds `127.0.0.1` by
default; non-localhost binds require `--allow-lan` because it executes local
commands. Runs commands as background jobs and surfaces stdout/stderr/exit
code/artifacts.

## Conventions

- New tools should be **grouped commands** (`command subcommand [options]`)
  following the existing Python command shape, not new standalone scripts.
  Legacy standalone scripts have been removed in favor of grouped equivalents.
- `--bc-metadata` output must be fast, side-effect free, and valid even when
  optional runtime dependencies are missing.
- After changing a command's subcommands/config, run `bashcommon doctor` and the
  test suite; update the `README.md` command table via `bashcommon list --markdown`.

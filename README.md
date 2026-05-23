
BASH_COMMON README
------------------

This is a collection of scripts to quickly set up a Bash environment. It has a bias
towards game development. Features (non-exhaustive) include:

- Directory bookmarks.
- Templates for new projects.
- Shortcuts/piping into text editors.
- Various command completions.
- Application launchers/helpers.

## User Features

- Portable Bash environment setup for macOS, Cygwin/Windows, and UNIX-like systems.
- Directory bookmarks.
- Project and script templates.
- Git, CMake, Unity, Android/ADB, Blender, Markdown, and video helpers.
- Platform-specific aliases and completions.
- Hierarchical `.bcconfig` configuration.
- `bcui`, a local browser UI for metadata-backed commands.

Implementation and future architecture notes live in [design.md](design.md). This
README is the user-facing reference for available features and commands.

## Command Inventory

### Shell Aliases And Functions

These are loaded into every interactive shell:

| Command | Purpose |
|---------|---------|
| `cls` | Clear the terminal. |
| `h` | Show shell history. |
| `..`, `...`, `....` | Move up one, two, or three directories. |
| `gg`, `ggf`, `ggs` | Git log graph aliases. |
| `bs <name>` | Save the current directory as a bookmark. |
| `g <name>` | Change directory to a saved bookmark. |
| `bp <name>` | Print a bookmark path. |
| `bd <name>` | Delete a bookmark. |
| `bl` | List bookmarks. |
| `tmpfile` | Generate a temporary filename. |
| `b2h <bytes>` | Convert a byte count to a human-readable size. |
| `duh [path]` | Show sorted disk usage and total size. |
| `tree` | Fallback directory tree printer if the real `tree` command is absent. |
| `command_exists <name>` | Test whether a command is available. |
| `colecho` | Print coloured terminal text. |
| `bc_cfg_get <section> <key> [fallback]` | Read a value from the effective `.bcconfig`. |
| `clr_*`, `clr_dump` | Terminal colour helpers. |

### Top-Level Commands

These commands live in the bash_common root and are available after `.profile`
adds `BC_INSTALL_DIR` to `PATH`:

| Command | Purpose |
|---------|---------|
| `bcinit` | Check/install dependencies, shell setup, and user config. |
| `bcconfig` | Show, query, and initialise `.bcconfig` settings. |
| `bcui` | Start the local browser UI for metadata-backed commands. |
| `bcup` | Update bash_common and, optionally, bundled completions. |
| `video` | Unified ffmpeg-backed video command with subcommands. |
| `markdown` | Run the `markdown2` command-line processor. |
| `mrename` | Generate a reviewed rename script from regex matches. |
| `newsh` | Create a new Bash script from a starter template. |
| `newgit` | Initialise a Git repo with standard attributes/ignore files. |
| `newunity` | Scaffold a Unity project directory and `.gitignore`. |
| `uadb` | Unity Android/ADB helper for install, run, uninstall, and logs. |
| `cm` | Configure/update a CMake build directory. |
| `cmdir` | Create a CMake build directory with a selected generator. |
| `uncrust` | Reformat C/C++ files with the bundled Uncrustify config. |
| `blend` | Launch Blender using bookmarked Blender paths. |
| `blpy` | Run Blender's bundled Python interpreter. |
| `cheat` | View or edit local cheat sheets. |
| `cookies` | Read, filter, and export Safari binary cookie files. |

### Video Tools

All video operations are unified under the `video` command (Python3, backed by ffmpeg):

- `video info FILE` — print codec, resolution, duration, and bitrate
- `video convert [-f FORMAT] [-o OUTPUT] FILE` — transcode to MP4 (H.264/AAC), WebM, MKV, or MOV
- `video concat [-o OUTPUT] FILE...` — join videos of the same format and resolution
- `video clamp [-s START] [-e END] [-o OUTPUT] FILE` — cut to a time range; `-s` and `-e` are optional (omit `-s` to start from the beginning, omit `-e` to go to the end)
- `video thumb [-t TIME] [-o OUTPUT] FILE` — extract a single frame as a PNG image
- `video catalog [-o OUTPUT] DIR` — scan a directory tree recursively and write a self-contained HTML report (name, size, duration, format, codec, resolution, fps, audio, bitrate)
- `video normalise [-n] [-f] DIR` — batch-normalise a directory tree to H.264/AAC MP4 at 720p; deinterlaces CRT/interlaced footage, upscales low-res content with lanczos, moves originals to a configurable backup directory. `-n` dry-run (writes a green/red HTML assessment report without converting), `-f` force re-process

Run `video <subcommand> -h` for per-subcommand help.

Dependencies: `ffmpeg` and `ffprobe` must be on PATH. Run `bcinit` to install.

### BC UI

`bcui` starts a local Flask web server for interacting with bash_common commands
in a browser:

```bash
bcui
```

By default it binds to `127.0.0.1:8765`. The UI discovers commands that expose
machine-readable metadata, shows their subcommands and options, runs them as
structured argument lists, and displays stdout, stderr, exit status, and known
artifacts.

Useful options:

```bash
bcui --host 127.0.0.1
bcui --port 8765
bcui --cwd /path/to/project
bcui --no-browser
```

The first metadata-backed command is `video`. More commands can appear in the
UI as they add metadata.

Dependency: Flask, installed by `bcinit` into bash_common's local `.venv`.

### Platform-Specific Commands

macOS/Darwin loads `darwin/_init.sh` and adds `darwin` to `PATH`:

| Command | Purpose |
|---------|---------|
| `ls`, `ll`, `la` | macOS listing aliases. |
| `ql <file>` | Preview a file with Finder Quick Look. |
| `dtop [0|1]` | Hide or show desktop icons. |
| `ddd [-f]` | Delete Xcode DerivedData. |
| `love ...` | Launch Love2D. |
| `kom ...` | Launch Komodo Edit. |
| `diffmerge ...` | Launch SourceGear DiffMerge. |
| `rmate ...` | Remote TextMate helper. |

Cygwin/Windows loads `cygwin/_init.sh` and adds `cygwin` to `PATH`:

| Command | Purpose |
|---------|---------|
| `ls`, `ll`, `la` | GNU-colour listing aliases. |
| `open ...` | Open paths/URLs with `cygstart`. |
| `apt-cyg ...` | Cygwin package manager helper. |

UNIX/Linux/BSD/WSL loads `unix/_init.sh` and adds `unix` to `PATH`:

| Command | Purpose |
|---------|---------|
| `ls`, `ll`, `la` | GNU-colour listing aliases. |

## Configuration

bash_common uses `.bcconfig` files — INI-format files that can live in any
directory, working like `.gitignore`: settings in a directory apply to that
directory and all its children, with closer-to-`pwd` files overriding parent
ones. The global defaults live at `~/.bcconfig`, created by `bcinit`.

### File format

`.bcconfig` is a standard INI file. Sections are named by command, with
sub-sections for subcommands separated by a dot:

```ini
[bash_common]
editor = mate

[video]
default_format = mp4

[video.convert]
video_codec  = libx264
video_preset = medium
video_crf    = 23
audio_codec  = aac
audio_bitrate = 128k

[video.thumb]
time = 00:00:05

[video.normalise]
target_width  = 1280
target_height = 720
original_dir  = /tmp/video-originals
deinterlace   = auto
```

### Directory override example

To use different encoding settings for a specific project, place a `.bcconfig`
file in the project directory:

```ini
# ~/projects/myfilm/.bcconfig
[video.convert]
video_crf    = 18
video_preset = slow

[video.normalise]
original_dir = ./originals
```

Only the keys you specify are overridden; everything else falls back to the
parent or global config.

### The `bcconfig` command

`bcconfig` shows the effective merged settings for your current location,
with each setting annotated by which file it came from:

```
$ bcconfig video

Sources (base → leaf):
  ~/.bcconfig
  ~/projects/myfilm/.bcconfig

[video.convert]
video_codec   = libx264    ~/.bcconfig
video_preset  = slow       ~/projects/myfilm/.bcconfig  ← overridden
video_crf     = 18         ~/projects/myfilm/.bcconfig  ← overridden
audio_codec   = aac        ~/.bcconfig
audio_bitrate = 128k       ~/.bcconfig
```

**Usage:**

```
bcconfig                              show all effective settings
bcconfig VIDEO                        filter to [VIDEO] and [VIDEO.*] sections
bcconfig --files                      list source files in load order
bcconfig --get video.convert.crf      print a single value
bcconfig --get video.convert.crf --fallback 23
bcconfig --init                       create .bcconfig in cwd with all sections
bcconfig --init video.normalise       create .bcconfig with only [video.normalise]
```

### Shell helper

The `bc_cfg_get` bash function (available in every interactive shell) reads a
single config value — useful in scripts and custom functions:

```bash
editor=$(bc_cfg_get bash_common editor mate)
vcodec=$(bc_cfg_get video.convert video_codec libx264)
```

Arguments: `bc_cfg_get <section> <key> [fallback]`

## Installing

Clone to `~/.bash_common` (the dot prefix keeps it hidden, consistent with other dot-files
in your home directory):

```bash
cd
git clone https://github.com/billyquith/bash_common.git .bash_common
```

After cloning, run `bcinit` to check and install all dependencies (ffmpeg, python3,
mediainfo, wget, and required Python packages):

```bash
~/.bash_common/bcinit
```

Pass `-c` to check without installing:

```bash
~/.bash_common/bcinit -c
```

Source the bash_common `.profile` and `.bashrc` from your home ones. In `~/.bash_profile`
source `.bash_common/.profile` and make sure your `.bashrc` is sourced:

```bash
[ -f ~/.bash_common/.profile ] && source ~/.bash_common/.profile  # source bash_common profile
[ -f ~/.bashrc ] && source ~/.bashrc                               # ensure .bashrc sourced
```

In your `~/.bashrc` ensure that `.bash_common/.bashrc` is sourced:

```bash
[ -f ~/.bash_common/.bashrc ] && source ~/.bash_common/.bashrc
```

## Platform Support

bash_common is designed to work across three platform families, selected automatically
at startup by inspecting `uname -s`:

| Platform | `BC_SYSTEM` | `BC_OS`   | Typical use                        |
|----------|-------------|-----------|-------------------------------------|
| macOS    | `darwin`    | `macos`   | Desktop development on Apple hardware |
| Windows  | `cygwin`    | `windows` | Cygwin terminal on Windows          |
| Linux / UNIX | `unix`  | `unix`    | Linux distros, FreeBSD, WSL, CI/CD  |

Platform-specific init scripts live in `darwin/_init.sh`, `cygwin/_init.sh`, and
`unix/_init.sh`. The `unix` label is intentionally broad — it is the catch-all for
anything that is not Darwin or Cygwin, including all Linux distributions (Ubuntu, Fedora,
Arch, etc.), BSDs, and WSL. There is no separate `linux` directory because there is no
behaviour that needs to be split at that level; distro differences (package managers,
etc.) are handled at install time by `bcinit`.

Each `_init.sh` sets platform-appropriate aliases and loads relevant completions. The
default `EDITOR` is also set per platform (TextMate on macOS, VS Code on Cygwin, `vi`
on UNIX).

## Environment

### Variables

- `EDITOR` : default text/source editor to use.
- `BC_INSTALL_DIR` : where this lives, bin dir.
- `BC_SYSTEM` : platform identifier (`darwin`, `cygwin`, or `unix`).
- `BC_OS` : OS family (`macos`, `windows`, or `unix`).

## Why Bash?

macOS switched its default shell to zsh in Catalina (10.15), but this was driven by
licensing: Bash 3.2 (2007) is the last version Apple could ship under GPLv2, and they
were unwilling to bundle the GPLv3-licensed Bash 4+. The switch was a licensing decision,
not a technical one.

Bash remains the right choice here because:

- **Portability** — Bash is the de facto standard on Linux, CI runners, Docker containers,
  and most cloud/server environments. Scripts written here work everywhere without
  modification.
- **Maturity** — Bash 5 is actively maintained and available via Homebrew on macOS
  (`brew install bash`). Over 40 years of shell scripting convention and tooling support it.
- **Ubiquity** — `#!/usr/bin/env bash` is universally understood. Most documentation,
  examples, and Stack Overflow answers are written for Bash.

macOS users should install a modern Bash and set it as their shell:

```bash
brew install bash
# Add /opt/homebrew/bin/bash (or /usr/local/bin/bash) to /etc/shells, then:
chsh -s /opt/homebrew/bin/bash
```

The system Bash at `/bin/bash` (3.2) is kept for compatibility with macOS scripts but
bash_common targets Bash 4+.

## Info

### .profile/.bashrc purposes

* `~/.bash_profile` should be super-simple and just load `.profile` and `.bashrc` (in that order).

* `~/.profile` has the stuff *not* specifically related to BASH, such as environment variables
  (PATH and friends).

* `~/.bashrc` has anything for interactive command line. Command prompt, EDITOR variable, bash
  aliases for my use

* Anything that should be available to graphical applications *or* to `sh` (or BASH invoked as sh)
  *must* be in `~/.profile`.

* `~/.bashrc` must not output anything.

* Anything that should be available only to login shells should go in `~/.profile`

* Ensure that `~/.bash_login` does not exist.


## Useful Resources

### Bash-it

 * <https://github.com/bash-it/bash-it>
 
### Binaries/Plugins
 
#### editorconfig
 
 - Textmate: https://github.com/Mr0grog/editorconfig-textmate
 - Xcode: https://github.com/MarcoSero/EditorConfig-Xcode
 
git clone --recurse-submodules https://github.com/MarcoSero/EditorConfig-Xcode.git
cd EditorConfig-Xcode
open EditorConfig.xcodeproj
 
 

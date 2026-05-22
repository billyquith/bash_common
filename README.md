
BASH_COMMON README
------------------

This is a collection of scripts to quickly set up a Bash environment. It has a bias
towards game development. Features (non-exhaustive) include:

- Directory bookmarks.
- Templates for new projects.
- Shortcuts/piping into text editors.
- Various command completions.
- Application launchers/helpers.

### Tools

- Bookmark directories
  - `g <name>` cd to bookmark
  - `bl` list bookmarks
  - `bp <name>` print bookmark directory
  - `bs <name>` save current directory as bookmark
  - `bd <name>` delete bookmark
- `markdown` Python markdown2 processor

### Video Tools

All video operations are unified under the `video` command (Python3, backed by ffmpeg):

- `video info FILE` — print codec, resolution, duration, and bitrate
- `video convert [-f FORMAT] [-o OUTPUT] FILE` — transcode to MP4 (H.264/AAC), WebM, MKV, or MOV
- `video concat [-o OUTPUT] FILE...` — join videos of the same format and resolution
- `video clamp [-s START] [-e END] [-o OUTPUT] FILE` — cut to a time range; `-s` and `-e` are optional (omit `-s` to start from the beginning, omit `-e` to go to the end)
- `video thumb [-t TIME] [-o OUTPUT] FILE` — extract a single frame as a PNG image
- `video catalog [-o OUTPUT] DIR` — scan a directory tree recursively and write a self-contained HTML report (name, size, duration, format, codec, resolution, fps, audio, bitrate)
- `video normalise [-n] [-f] DIR` — batch-normalise a directory tree to H.264/AAC MP4 at 720p; deinterlaces CRT/interlaced footage, upscales low-res content with lanczos, moves originals to a configurable backup directory. `-n` dry-run, `-f` force re-process

Run `video <subcommand> -h` for per-subcommand help.

Dependencies: `ffmpeg` and `ffprobe` must be on PATH. Run `bcinit` to install.

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
bcconfig                           show all effective settings
bcconfig VIDEO                     filter to [VIDEO] and [VIDEO.*] sections
bcconfig --files                   list source files in load order
bcconfig --get video.convert.crf   print a single value
bcconfig --get video.convert.crf --fallback 23
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
 
 

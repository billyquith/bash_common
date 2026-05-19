
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
- `video trim -s START -e END [-o OUTPUT] FILE` — cut to a time range (HH:MM:SS or seconds)
- `video thumb [-t TIME] [-o OUTPUT] FILE` — extract a single frame as a PNG image

Run `video <subcommand> -h` for per-subcommand help.

Dependencies: `ffmpeg` and `ffprobe` must be on PATH. Run `bcinit` to install.
  
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
 
 


README
------

This is a collection of BASH scripts to enhance a basic BASH environment. Features (non-exhaustive) added:

- Directory bookmarks.
- Templates for new projects.
- Shortcuts/piping into text editors.
- Various command completions.

## Installing

Clone/download to a directory (`~/bash_shared` in this example).

Add to POSIX `.bash_profile` :-

```bash
[ -f ~/bash_shared/.profile ] && source ~/bash_shared/.profile

[ -f ~/.bashrc ] && source ~/.bashrc
```

`.bashrc` :-

```bash
[ -f ~/bash_shared/.bashrc ] && source ~/bash_shared/.bashrc
```

## Environment

### Variables

- `EDITOR` : default text/source editor to use.
- `BS_INSTALL_DIR` : where this lives, bin dir.

### Commands

- x

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
 
 

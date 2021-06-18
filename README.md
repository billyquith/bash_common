
BASH_COMMON README
------------------

This is a collection of scripts to quickly set up a BASH environment. It has a bias 
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
  
## Installing

Clone/download to a directory (`~/bash_common` in this example). bash_common needs
initialising to add things like environment variables, paths, and completions.

```bash
    cd
    git clone https://github.com/billyquith/bash_common.git
```

Source the bash_common `.profile` and `.bashrc` from your home ones. In `~/.bash_profile` 
source `bash_common/.profile` and make sure your `.bashrc` is sourced:

```bash
[ -f ~/bash_common/.profile ] && source ~/bash_common/.profile  # source bash_commmon profile
[ -f ~/.bashrc ] && source ~/.bashrc                            # ensure .bashrc sourced
```

In your `~/.bashrc` ensure that `bash_common/.bashrc` is sourced:

```bash
[ -f ~/bash_common/.bashrc ] && source ~/bash_common/.bashrc
```

## Environment

### Variables

- `EDITOR` : default text/source editor to use.
- `BC_INSTALL_DIR` : where this lives, bin dir.

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
 
 

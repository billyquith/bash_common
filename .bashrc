# bash_common/.bashrc
#
# Purpose: This is called by interactive shells (e. terminal) and should contain
# graphical formatting stuff.

# :-    https://www.gnu.org/software/bash/manual/bash.html#Shell-Parameter-Expansion

if [ -z "$BC_INSTALL_DIR" ]; then
    echo "ERROR, BC_INSTALL_DIR not set" # have your sourced .profile?
    exit 1
fi

shopt -s histappend
shopt -s cmdhist
export HISTCONTROL="erasedups:ignoreboth" # ignore duplicates
export HISTIGNORE="&:[ ]*:exit"
export HISTFILESIZE=500000
export HISTSIZE=10000

alias ls='ls -GF'
alias ll='ls -hl'
alias la='ls -AF'
alias cls='clear'
alias h='history'

alias ..='cd ..'         # Go up one directory
alias ...='cd ../..'     # Go up two directories
alias ....='cd ../../..' # Go up three directories

# Platform config
case `uname -o` in
Cygwin)
	export BC_SYSTEM=cygwin
	export BC_OS=windows
	export EDITOR=code  # VS Code
	;;
Darwin)
	export BC_SYSTEM=darwin
	export BC_OS=macos
	export EDITOR=mate  # Textmate
	;;
 *)
	export BC_SYSTEM=unix
	export BC_OS=unix
	export EDITOR=vi
	;;
esac

# functions & commands
source $BC_INSTALL_DIR/bash/colour.sh
source $BC_INSTALL_DIR/bash/apps.sh
source $BC_INSTALL_DIR/bash/bookmark.sh
source $BC_INSTALL_DIR/bash/helpers.sh

#### Platform specific ####

if [ -d ./$BC_SYSTEM ]; then
	export PATH=$PATH:$BC_INSTALL_DIR/$BC_SYSTEM
	source ./$BC_SYSTEM/_init.sh
fi

case $BC_SYSTEM in
cygwin)
	export PATH=$PATH:$BC_INSTALL_DIR/cygwin
	;;
darwin)
	source $BC_INSTALL_DIR/completion/brew.completion.bash
    ;;
*)	source $BC_INSTALL_DIR/bash/$BC_SYSTEM.sh 
	;;
esac

source $BC_INSTALL_DIR/completion/adb.completion.bash
#source $BC_INSTALL_DIR/completion/git.completion.bash
source $BC_INSTALL_DIR/completion/p4.completion.bash

export PS1="$(clr_escape_wrap '\w>' '36') "

echo "$(clr_magenta "Welcome to") $(clr_escape bash_common $CLR_YELLOW $CLR_BOLD) 8D"

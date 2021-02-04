# bin_shared/.bashrc
#
# Purpose: This is called by interactive shells (e. terminal) and should contain
# graphical formatting stuff.

# :-    https://www.gnu.org/software/bash/manual/bash.html#Shell-Parameter-Expansion

if [ -z "$BIN_SHARED" ]; then
    echo "ERROR, BIN_SHARED not set"
    exit 1
fi

export EDITOR=mate

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

source $BIN_SHARED/bash/colour.sh
source $BIN_SHARED/bash/apps.sh
source $BIN_SHARED/bash/bookmark.sh
source $BIN_SHARED/bash/helpers.sh

if [ "$(uname)" == "Darwin" ]; then
    source $BIN_SHARED/bash/xcode.sh
    source $BIN_SHARED/bash/mac.sh
fi

source $BIN_SHARED/completion/brew.completion.bash
source $BIN_SHARED/completion/git.completion.bash

source $BIN_SHARED/git-subrepo/.rc

export PS1="$(clr_escape '\w>' '36') "

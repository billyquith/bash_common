# Windows Cygwin specific functionality

source $BC_INSTALL_DIR/completion/fbuild.completion.bash
source $BC_INSTALL_DIR/completion/p4.completion.bash

alias ls='ls --color=auto -F'
alias ll='ls -hl'
alias la='ls -A'

function open {
    cygstart $*
}


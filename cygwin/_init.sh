# Windows Cygwin specific functionality

source $BC_INSTALL_DIR/completion/fbuild.completion.bash
source $BC_INSTALL_DIR/completion/p4.completion.bash

function open {
    cygstart $*
}


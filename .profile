# bin_shared/.profile
# 
# This is called by a login shell and should contain env variables. Not called by terminal.
#
# call: [ -f ~/bin_shared/.profile ] && source ~/bin_shared/.profile

DIR=$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)

export BIN_SHARED=$DIR
export PATH=$PATH:$BIN_SHARED


# MacOS Darwin specific functionality

source $BC_INSTALL_DIR/completion/brew.completion.bash

# Use Finder's Quick Look on a file (^C or space to close)
alias ql='qlmanage -p 2>/dev/null'

# dtop [0|1]    enable/disable desktop icons
function dtop {
    local state="true"
    local opt=${1:-"0"}
    if [ $opt -eq 0 ]; then state="false"; fi
    
    echo "Show desktop: $state"
    defaults write com.apple.finder CreateDesktop $state
    killall Finder    
}


# Xcode command-line helpers

# Delete derived data. Good to do occasionally.
function ddd
{
  local DERIVED=~/Library/Developer/Xcode/DerivedData    
  pushd $DERIVED
  echo In $(pwd)
  
  du -ch -d1 .
    
  if [ "$1" == "-f" ]; then      
    #Sometimes, 1 file remains, so loop until no files remain
    local numRemainingFiles=1
    while [ $numRemainingFiles -gt 0 ]; do
      #Delete the files, recursively
      rm -rf *
  
      #Update file count
      numRemainingFiles=`ls | wc -l`
    done
  else
    rm -rf *  # !!!
  fi

  popd
  echo Done
}


# TODO- Start love2d
declare -fx love
function love   # ...
{
    open -n -a "Love" "$@"
}

# TODO- Pass file to komodo. Can also pipe in from stdin.
declare -fx kom
function kom    #[filename]
{
    local CMD='/Applications/Komodo Edit 9.app/Contents/MacOS/komodo'
    local ARGS="$@"
    
    if [ ! -t 0 ]; then
        # piping in
        local FILE=$(tmp_file kom /tmp)
        cat > "$FILE"
        ARGS="$FILE"
    fi
    
    if [ -z "$ARGS" ]; then
        $("$CMD")
    else
        $("$CMD" $ARGS)
    fi
}


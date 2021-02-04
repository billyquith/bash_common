#!/bin/bash


function tmp_file #name [where]
{
    local WHAT=$1
    local DIR=${2:="/tmp"}
    echo $(mktemp $DIR/$WHAT.XXXXXX)
}

# Start love2d
declare -fx love
function love   # ...
{
    open -n -a "Love" "$@"
}

# Pass file to komodo. Can also pipe in from stdin.
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


# Make a tempfile name
function tmpfile {
    echo $(mktemp /tmp/temp.$$.XXXXXX.tmp)
}

# Convert a number to human readable
function b2h {
    b=${1:-0}; d=''; s=0; S=(Bytes {K,M,G,T,E,P,Y,Z}iB)
    while ((b > 1024)); do
        d="$(printf ".%02d" $((b % 1024 * 100 / 1024)))"
        b=$((b / 1024))
        let s++
    done
    echo "$b$d ${S[$s]}"
}

# Output disk usage in useful format
function duh {    
    du "$@" | sort -gr | head -n 50
    echo
    du -sh "$@"
}

# print directory hierarchy
if [ ! -x "$(which tree 2>/dev/null)" ]
then
    function tree
    {
        find . -print | sed -e 's;[^/]*/;|____;g;s;____|; |;g'
    }
fi


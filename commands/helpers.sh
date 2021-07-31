
# Make a tempfile name
#   - TMPFILE=/tmp/data$(tmpfile)
function tmpfile
{
    echo $(mktemp XXXXXXXX.tmp)
}
export -f tmpfile

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
export -f b2h

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

# > if command_exists touch; then ... fi
function command_exists
{
    [ -x "$(command -v $1)" ]   # returns true/false
}
export -f command_exists

# colour echo output: colecho -red "red" -green "green"
function colecho ()
{
	while [ $# -ne 0 ];
	do
		case $1 in
		# foreground
		-bk|-black) echo -en "\e[0;30m" ;;
		-lr|-lightred) echo -en "\e[1;31m" ;;
		-lg|-lightgreen) echo -en "\e[1;32m" ;;
		-rd|-red) echo -en "\e[0;31m" ;;
		-gr|-green) echo -en "\e[0;32m" ;;
		-ye|-yellow) echo -en "\e[1;33m" ;;
		-lb|-lightblue) echo -en "\e[1;34m" ;;
		-br|-brown) echo -en "\e[0;33m" ;;
		-bl|-blue) echo -en "\e[0;34m" ;;
		-lp|-lightpurple) echo -en "\e[1;35m" ;;
		-pu|-purple) echo -en "\e[0;35m" ;;
		-lc|-lightcyan) echo -en "\e[1;36m" ;;
		-cy|-cyan) echo -en "\e[0;36m" ;;
		-gr|-grey) echo -en "\e[0;37m" ;;
		-dg|-darkgrey) echo -en "\e[1;30m" ;;
		-wh|-white) echo -en "\e[1;37m" ;;

		# background
		-bgblack) echo -en "\e[40m" ;;
		-bgred) echo -en "\e[41m" ;;
		-bggreen) echo -en "\e[42m" ;;
		-bgbrown) echo -en "\e[43m" ;;
		-bgblue) echo -en "\e[44m" ;;
		-bgpurple) echo -en "\e[45m" ;;
		-bgcyan) echo -en "\e[46m" ;;
		-bggrey) echo -en "\e[47m" ;;

		# effects
		-normal) echo -en "\e[0m" ;;
		-b|-bold) echo -en "\e[1m" ;;
		-ul) echo -en "\e[4m" ;;
		-blink) echo -en "\e[5m" ;;
		-reverse) echo -en "\e[7m" ;; # reverse fg/bg

		-code) shift; echo -en "\e[$1m" ;;  # -c <code>
		-reset) echo -en "\e[0m" ;;
		-tab) echo -en "\t" ;;

		-*) echo -n "???$1???" ;; # unrecognised

		*) echo -n "$1" ;;
		esac
		shift
	done
	echo -e "\e[0m"
}
export -f colecho

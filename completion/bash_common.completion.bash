# Generic completion for metadata-backed bash_common commands.

__bc_meta_json() {
    local cmd="$1"
    local resolved mtime key cache tmp

    resolved="$(command -v "$cmd" 2>/dev/null)" || return 1
    if mtime="$(stat -f %m "$resolved" 2>/dev/null)"; then
        :
    elif mtime="$(stat -c %Y "$resolved" 2>/dev/null)"; then
        :
    else
        mtime="unknown"
    fi

    key="$(printf '%s_%s' "$(basename "$resolved")" "$mtime" | tr -c 'A-Za-z0-9_' '_')"
    cache="${TMPDIR:-/tmp}/bash_common_meta_${USER:-user}_${key}.json"
    if [ -s "$cache" ]; then
        cat "$cache"
        return 0
    fi

    tmp="${cache}.$$"
    if "$resolved" --bc-metadata >"$tmp" 2>/dev/null; then
        mv "$tmp" "$cache"
        cat "$cache"
    else
        rm -f "$tmp"
        return 1
    fi
}

__bc_meta_query() {
    local cmd="$1"
    local mode="$2"
    local subcommand="${3:-}"
    local token="${4:-}"
    local meta

    if ! command -v python3 >/dev/null 2>&1; then
        return 1
    fi

    meta="$(__bc_meta_json "$cmd")"
    BC_META_JSON="$meta" python3 - "$mode" "$subcommand" "$token" <<'PY'
import json
import os
import sys

mode, sub_name, token = sys.argv[1:4]
try:
    data = json.loads(os.environ.get("BC_META_JSON", ""))
except Exception:
    sys.exit(1)

subcommands = data.get("subcommands", [])

if mode == "subcommands":
    for sub in subcommands:
        print(sub.get("name", ""))
    sys.exit(0)

sub = next((s for s in subcommands if s.get("name") == sub_name), None)
if not sub:
    sys.exit(0)

options = sub.get("options", [])
if mode == "options":
    for opt in options:
        if opt.get("flag"):
            print(opt["flag"])
        if opt.get("short_flag"):
            print(opt["short_flag"])
    sys.exit(0)

if mode == "option-kind":
    for opt in options:
        if token in (opt.get("flag"), opt.get("short_flag")):
            print(opt.get("kind", "string"))
            for choice in opt.get("choices", []):
                print(choice)
            sys.exit(0)
    sys.exit(0)

if mode == "arg-kind":
    args = sub.get("args", [])
    if args:
        print(args[-1].get("kind", "path"))
    sys.exit(0)
PY
}

__bc_complete_path_for_kind() {
    local kind="$1"
    local cur="$2"

    case "$kind" in
        directory)
            COMPREPLY=( $(compgen -d -- "$cur") )
            ;;
        path|path-list|"")
            COMPREPLY=( $(compgen -f -- "$cur") )
            ;;
        *)
            COMPREPLY=()
            ;;
    esac
}

__bc_complete_metadata_command() {
    local cmd="${COMP_WORDS[0]}"
    local cur="${COMP_WORDS[COMP_CWORD]}"
    local prev=""
    local subcommand=""

    COMPREPLY=()

    if [ "$COMP_CWORD" -gt 0 ]; then
        prev="${COMP_WORDS[COMP_CWORD-1]}"
    fi

    if [ "$COMP_CWORD" -eq 1 ]; then
        COMPREPLY=( $(compgen -W "$(__bc_meta_query "$cmd" subcommands)" -- "$cur") )
        return 0
    fi

    subcommand="${COMP_WORDS[1]}"

    if [[ "$prev" == -* ]]; then
        local info kind choices
        info="$(__bc_meta_query "$cmd" option-kind "$subcommand" "$prev")"
        kind="$(printf '%s\n' "$info" | sed -n '1p')"
        choices="$(printf '%s\n' "$info" | sed '1d')"
        if [ "$kind" != "boolean" ] && [ -n "$kind" ]; then
            if [ "$kind" = "choice" ]; then
                COMPREPLY=( $(compgen -W "$choices" -- "$cur") )
            else
                __bc_complete_path_for_kind "$kind" "$cur"
            fi
            return 0
        fi
    fi

    if [[ "$cur" == -* ]]; then
        COMPREPLY=( $(compgen -W "$(__bc_meta_query "$cmd" options "$subcommand")" -- "$cur") )
        return 0
    fi

    __bc_complete_path_for_kind "$(__bc_meta_query "$cmd" arg-kind "$subcommand")" "$cur"
    return 0
}

__bc_register_metadata_completions() {
    local dir="${BC_INSTALL_DIR:-}"
    local path name

    [ -n "$dir" ] || return 0
    [ -d "$dir" ] || return 0

    for path in "$dir"/*; do
        [ -f "$path" ] || continue
        [ -x "$path" ] || continue
        grep -q -- "--bc-metadata\|def bc_metadata" "$path" 2>/dev/null || continue
        name="$(basename "$path")"
        complete -o default -F __bc_complete_metadata_command "$name"
    done
}

__bc_register_metadata_completions

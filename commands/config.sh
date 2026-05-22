# bash_common/commands/config.sh
#
# Config helpers for reading .bcconfig values from within bash scripts.
# Sourced by .bashrc into every interactive shell.

# bc_cfg_get <section> <key> [fallback]
#
# Print the effective value of section.key from the .bcconfig chain
# (from ~ down to the current directory). Exits non-zero if the key is
# not found and no fallback is provided.
#
# Example:
#   editor=$(bc_cfg_get bash_common editor mate)
#   vcodec=$(bc_cfg_get video.convert video_codec libx264)
bc_cfg_get() {
    local section="$1"
    local key="$2"
    local fallback="${3:-}"
    if [ -n "$fallback" ]; then
        bcconfig --get "${section}.${key}" --fallback "$fallback"
    else
        bcconfig --get "${section}.${key}"
    fi
}

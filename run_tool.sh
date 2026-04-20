#!/usr/bin/env bash

# raise error, raise unbound vars
set -Eeuo pipefail

# change the word-splitting dleimiter to newline + tab only
IFS=$'\n\t'

msg_space() {
    echo -e "\n\n"
}

msg_info() {
    echo -e "\033[34m[~] $*\033[0m"
}

msg_error() {
    echo -e "\033[31m[-] $*\033[0m"
}

msg_succ() {
    echo -e "\033[32m[+] $*\033[0m"
}

OUTPUT="bin_output"

# Accept an optional tree-sitter mode: --tree-sitter (all), --brief (subset), or none.
TS_FLAG=""
case "${1:-}" in
    --tree-sitter|--brief)
        TS_FLAG="$1"
        ;;
    "")
        ;;
    *)
        msg_error "Unknown argument: $1"
        msg_error "Usage: $0 [--tree-sitter | --brief]"
        exit 1
        ;;
esac

msg_info "Creating output directory"
rm -rf "${OUTPUT}"
mkdir "${OUTPUT}"
msg_succ "Created ${OUTPUT}. Going to execute tool against this directory"

msg_info "Loading nix environment and running git-sync${TS_FLAG:+ ${TS_FLAG}}..."
if [[ -n "${TS_FLAG}" ]]; then
    nix develop -c uv run git-sync "${TS_FLAG}" -d "${OUTPUT}"
else
    nix develop -c uv run git-sync -d "${OUTPUT}"
fi

msg_info "Taring folder and cleanin up"
tar -czf "${OUTPUT}.tar.gz" "${OUTPUT}/" 
rm -rf "${OUTPUT}"

msg_succ "Done. ${OUTPUT}.tar.gz contains all the files"

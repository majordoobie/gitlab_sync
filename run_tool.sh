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

msg_info "Creating output directory"
rm -rf "${OUTPUT}"
mkdir "${OUTPUT}"
msg_succ "Created ${OUTPUT}. Going to execute tool against this directory"

msg_info "Loading nix environment and running git-sync..."
nix develop -c uv run git-sync -d "${OUTPUT}"
msg_succ "done"

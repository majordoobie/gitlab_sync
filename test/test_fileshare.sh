#!/usr/bin/env bash
# Integration test for ~/.config/nvim/lua/config/fileshare.lua
#
# Stubs a fake fileshare + plugin git repo under /tmp, overrides FILESHARE_ROOT
# via the NVIM_FILESHARE_ROOT env var, and exercises copy_tag_matched_binary in
# a headless nvim. Covers: happy path, missing binary, no tag, codediff-style
# post hook that copies a sidecar (libgomp).
#
# Run: bash test/test_fileshare.sh

set -Eeuo pipefail
IFS=$'\n\t'

ROOT=/tmp/fileshare_test
NVIM_CONFIG="${HOME}/.config/nvim"

PASS=0
FAIL=0

pass() { printf '  \033[32m✓ %s\033[0m\n' "$1"; PASS=$((PASS + 1)); }
fail() { printf '  \033[31m✗ %s\033[0m\n' "$1"; FAIL=$((FAIL + 1)); }
header() { printf '\n\033[1m=== %s ===\033[0m\n' "$1"; }

run_lua() {
    nvim --headless \
        --cmd "set rtp+=${NVIM_CONFIG}" \
        -c "lua $1" \
        -c 'q' 2>&1 | grep -v 'telescope-fzf-native' || true
}

setup() {
    rm -rf "$ROOT"
    mkdir -p "$ROOT/share/blink.cmp" "$ROOT/share/codediff.nvim"

    # Fileshare binaries the "real" ones would live here
    printf 'FAKE_BINARY_V1.0.0' > "$ROOT/share/blink.cmp/blink.cmp_v1.0.0.so"
    printf 'FAKE_BINARY_V0.9.0' > "$ROOT/share/blink.cmp/blink.cmp_v0.9.0.so"
    printf 'FAKE_VSCODE_V2.43.15' > "$ROOT/share/codediff.nvim/codediff.nvim-libvscode_v2.43.15.so"
    printf 'FAKE_LIBGOMP_V2.43.15' > "$ROOT/share/codediff.nvim/codediff.nvim-libgomp_v2.43.15.so.1"
}

make_plugin_repo() {
    # make_plugin_repo <dir> <tag1> [<tag2>]
    # If two tags given, they're placed on DIFFERENT commits so describe --exact-match
    # resolves to the newer one.
    local dir=$1 tag1=$2 tag2=${3:-}
    rm -rf "$dir"
    mkdir -p "$dir"
    (
        cd "$dir"
        git init -q
        git -c user.email=t@t -c user.name=t commit -q --allow-empty -m "$tag1"
        git tag "$tag1"
        if [[ -n "$tag2" ]]; then
            git -c user.email=t@t -c user.name=t commit -q --allow-empty -m "$tag2"
            git tag "$tag2"
        fi
    )
}

export NVIM_FILESHARE_ROOT="$ROOT/share"
setup

# ─────────────────────────────────────────────────────────────────────────────
header "Test 1: happy path — tag matches available binary"
make_plugin_repo "$ROOT/plugin" v1.0.0

out=$(run_lua "
local fs = require('config.fileshare')
local ok = fs.copy_tag_matched_binary({
    name = 'blink.cmp',
    plugin_path = '$ROOT/plugin',
    subdir = 'blink.cmp',
    source_tmpl = 'blink.cmp_%s.so',
    dest = function(_) return '$ROOT/plugin/target/release/libblink_cmp_fuzzy.so' end,
    post = function(tag, path) print('POST_FIRED:' .. tag .. ':' .. path) end,
})
print('RETURNED:' .. tostring(ok))
")
echo "$out"

[[ -f "$ROOT/plugin/target/release/libblink_cmp_fuzzy.so" ]] && pass "dest file created" || fail "dest file missing"
[[ "$(cat $ROOT/plugin/target/release/libblink_cmp_fuzzy.so)" == "FAKE_BINARY_V1.0.0" ]] && pass "dest contents correct" || fail "dest contents wrong"
grep -q "POST_FIRED:v1.0.0:$ROOT/plugin" <<< "$out" && pass "post hook received (tag, path)" || fail "post hook args wrong"
grep -q "RETURNED:true" <<< "$out" && pass "returns true" || fail "did not return true"
grep -q "Copying blink.cmp v1.0.0" <<< "$out" && pass "logs 'Copying…' message" || fail "missing copy message"
grep -q "✅ blink.cmp v1.0.0" <<< "$out" && pass "logs success message" || fail "missing success message"

# ─────────────────────────────────────────────────────────────────────────────
header "Test 2: tag has no matching binary on fileshare"
make_plugin_repo "$ROOT/plugin" v1.0.0 v2.0.0  # HEAD on v2.0.0, share only has v0.9/v1.0

out=$(run_lua "
local fs = require('config.fileshare')
local ok = fs.copy_tag_matched_binary({
    name = 'blink.cmp',
    plugin_path = '$ROOT/plugin',
    subdir = 'blink.cmp',
    source_tmpl = 'blink.cmp_%s.so',
    dest = function(_) return '$ROOT/plugin/target/release/libblink_cmp_fuzzy.so' end,
})
print('RETURNED:' .. tostring(ok))
")
echo "$out"

grep -q "RETURNED:false" <<< "$out" && pass "returns false" || fail "should have returned false"
grep -q "no binary for v2.0.0" <<< "$out" && pass "reports missing tag" || fail "missing-tag message absent"
grep -q "Available:.*v0.9.0.*v1.0.0" <<< "$out" && pass "lists available binaries" || fail "did not list alternatives"

# ─────────────────────────────────────────────────────────────────────────────
header "Test 3: plugin HEAD is not on any tag"
make_plugin_repo "$ROOT/plugin" v1.0.0
(cd "$ROOT/plugin" && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m "untagged work")

out=$(run_lua "
local fs = require('config.fileshare')
local ok = fs.copy_tag_matched_binary({
    name = 'blink.cmp',
    plugin_path = '$ROOT/plugin',
    subdir = 'blink.cmp',
    source_tmpl = 'blink.cmp_%s.so',
    dest = function(_) return '$ROOT/plugin/target/release/libblink_cmp_fuzzy.so' end,
})
print('RETURNED:' .. tostring(ok))
")
echo "$out"

grep -q "RETURNED:false" <<< "$out" && pass "returns false" || fail "should have returned false"
grep -q "is not on a git tag" <<< "$out" && pass "reports untagged HEAD" || fail "untagged-HEAD message absent"

# ─────────────────────────────────────────────────────────────────────────────
header "Test 4: codediff-style post hook copies libgomp sidecar"
make_plugin_repo "$ROOT/plugin2" v2.43.15

out=$(run_lua "
local fs = require('config.fileshare')
local ok = fs.copy_tag_matched_binary({
    name = 'codediff',
    plugin_path = '$ROOT/plugin2',
    subdir = 'codediff.nvim',
    source_tmpl = 'codediff.nvim-libvscode_%s.so',
    dest = function(tag)
        local v = tag:gsub('^v','')
        return '$ROOT/plugin2/libvscode_diff_' .. v .. '.so'
    end,
    post = function(tag, path)
        local src = fs.fileshare_root() .. '/codediff.nvim/codediff.nvim-libgomp_' .. tag .. '.so.1'
        if vim.uv.fs_stat(src) then
            vim.uv.fs_copyfile(src, path .. '/libgomp.so.1')
            print('LIBGOMP_COPIED')
        end
    end,
})
print('RETURNED:' .. tostring(ok))
")
echo "$out"

[[ -f "$ROOT/plugin2/libvscode_diff_2.43.15.so" ]] && pass "main binary copied" || fail "main binary missing"
[[ -f "$ROOT/plugin2/libgomp.so.1" ]] && pass "libgomp sidecar copied" || fail "libgomp missing"
[[ "$(cat $ROOT/plugin2/libvscode_diff_2.43.15.so)" == "FAKE_VSCODE_V2.43.15" ]] && pass "main binary contents" || fail "main binary contents wrong"
[[ "$(cat $ROOT/plugin2/libgomp.so.1)" == "FAKE_LIBGOMP_V2.43.15" ]] && pass "libgomp contents" || fail "libgomp contents wrong"
grep -q "RETURNED:true" <<< "$out" && pass "returns true" || fail "did not return true"

# ─────────────────────────────────────────────────────────────────────────────
header "Summary"
printf '  %s passed, %s failed\n' "$PASS" "$FAIL"
rm -rf "$ROOT"
[[ $FAIL -eq 0 ]] || exit 1

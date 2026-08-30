#!/usr/bin/env bash
# Install the WezTerm trial from WSL. Idempotent; re-run any time.
#   1. copy wezterm.lua to %USERPROFILE%\.wezterm.lua
#   2. link + enable wezterm-watch.service, which keeps step 1 current on every save
# WezTerm itself is installed on the Windows side:  winget install wez.wezterm.nightly
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=wezterm-paths.sh
source "$HERE/wezterm-paths.sh"

copied=0
if cp -f "$HERE/wezterm.lua" "$WEZTERM_DST" 2>/dev/null; then
  copied=1; echo "installed $WEZTERM_DST"
else
  echo "cannot write $WEZTERM_DST now (/mnt/c or interop down); the watcher retries every 10 s" >&2
fi

if ! systemctl --user cat wezterm-watch.service >/dev/null 2>&1; then
  systemctl --user link "$HERE/wezterm-watch.service"
fi
systemctl --user daemon-reload
systemctl --user enable --now wezterm-watch.service
systemctl --user --no-pager --lines=3 status wezterm-watch.service || true
[[ $copied -eq 1 ]]

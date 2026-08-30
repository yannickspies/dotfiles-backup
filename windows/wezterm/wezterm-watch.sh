#!/usr/bin/env bash
# Mirror ~/dotfiles/windows/wezterm/wezterm.lua to %USERPROFILE%\.wezterm.lua on every
# save. WezTerm watches that local file and hot-reloads; it cannot watch a file inside
# WSL (microsoft/WSL#7674). Polls mtime every 2 s: no inotify-tools needed, and one
# stat per 2 s is free. Runs as the wezterm-watch systemd user service.
set -u
# shellcheck source=wezterm-paths.sh
source "$(dirname "$(readlink -f "$0")")/wezterm-paths.sh"

sync_once() {
  # Write to a temp file then rename, so WezTerm never reloads a half-written config.
  cp -f "$WEZTERM_SRC" "$WEZTERM_DST.tmp" && mv -f "$WEZTERM_DST.tmp" "$WEZTERM_DST"
}

last=''
failing=0
while true; do
  cur="$(stat -c %Y "$WEZTERM_SRC" 2>/dev/null || true)"
  if [[ -n "$cur" && "$cur" != "$last" ]]; then
    if sync_once 2>/dev/null; then
      last="$cur"
      [[ $failing -eq 1 ]] && echo "/mnt/c is back"
      failing=0
      echo "synced $WEZTERM_SRC -> $WEZTERM_DST"
    else
      # Log once, then retry silently every 10 s until /mnt/c answers again.
      [[ $failing -eq 0 ]] && echo "copy to $WEZTERM_DST failed (/mnt/c unreachable?); retrying every 10 s" >&2
      failing=1
      sleep 10
      continue
    fi
  fi
  sleep 2
done

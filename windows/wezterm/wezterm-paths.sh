# Sourced by apply.sh and wezterm-watch.sh. Resolves where the Windows copy goes.
# Override with WEZTERM_WIN_HOME=/mnt/c/Users/<name> if interop is unavailable.
wezterm_win_home() {
  if [[ -n "${WEZTERM_WIN_HOME:-}" ]]; then
    printf '%s\n' "$WEZTERM_WIN_HOME"; return
  fi
  local up
  up="$(cmd.exe /c 'echo %USERPROFILE%' 2>/dev/null | tr -d '\r')"
  if [[ -n "$up" ]]; then
    wslpath -u "$up" 2>/dev/null && return
  fi
  printf '%s\n' '/mnt/c/Users/yanni' # last resort: the path ../README.md documents
}
WEZTERM_SRC="${WEZTERM_SRC:-$HOME/dotfiles/windows/wezterm/wezterm.lua}"
WEZTERM_DST="$(wezterm_win_home)/.wezterm.lua"

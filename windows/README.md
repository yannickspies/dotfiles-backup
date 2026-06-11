# Windows terminal config (WSL host side)

Config for the terminal running on the Windows side of this WSL setup.
It lives on NTFS, so GNU Stow can't symlink it — apply by copying.

## Status

| Terminal | Role | Live config location (Windows) |
|----------|------|--------------------------------|
| **Windows Terminal** | Primary (only maintained terminal) | `%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json` |
| WezTerm | **Retired** (clipboard paste broke into the WSL pty) | `wezterm/wezterm.lua.retired` kept for reference — its comments document the paste diagnosis |
| Alacritty | **Dropped** (no double maintenance) | a working WSL config may still sit at `%APPDATA%\alacritty\alacritty.toml`, but it is not tracked here |

Ghostty and kitty were considered but have no Windows builds.

## Apply (from WSL)

```sh
cp windows/windows-terminal/settings.json \
  "/mnt/c/Users/yanni/AppData/Local/Packages/Microsoft.WindowsTerminal_8wekyb3d8bbwe/LocalState/settings.json"
```

Note: Windows Terminal rewrites/normalizes its settings.json on load
(reorders keys, renames some to canonical form). After changing settings
via the WT UI, sync back with the copy in the other direction.

## Theme

**Catppuccin Mocha** everywhere, applied 2026-06-11:

- Windows Terminal: `Catppuccin Mocha` color scheme + window/tab theme
  (both embedded in settings.json, from catppuccin/windows-terminal)
- tmux: `catppuccin/tmux#v2.1.3` via TPM (`prefix + I` to install)
- Neovim: `catppuccin/nvim` (flavour mocha) in both nvim configs

## Fonts

- Text: **CommitMono** (plain, no glyphs) — installed per-user
- Icons/Nerd Font glyphs: **JetBrainsMono NFM** — installed per-user
- Windows Terminal does per-glyph fallback via the comma list
  `"face": "CommitMono, JetBrainsMono NFM"` (equivalent of wezterm's
  `font_with_fallback`).

## Paste redundancy (ported from the wezterm fix)

Three paste triggers so a single shadowed hotkey can never lock you out
again: `Ctrl+V` / `Ctrl+Shift+V`, `Shift+Insert`, and right-click
(WT default mouse behavior).

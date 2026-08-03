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

- Windows Terminal: `Catppuccin Mocha Deep` color scheme + window/tab theme
  (both embedded in settings.json; derived from catppuccin/windows-terminal)
- tmux: `catppuccin/tmux#v2.1.3` via TPM (`prefix + I` to install)
- Neovim: `catppuccin/nvim` (flavour mocha) in both nvim configs

### Catppuccin Mocha Deep (2026-07-27)

A darker, higher-contrast variant tuned for code + Claude Code. Stock
`Catppuccin Mocha` is kept in settings.json so it can be re-selected from
the UI at any time.

| Change | From | To | Why |
|---|---|---|---|
| `background` | `#1E1E2E` (Base) | `#11111B` (Crust) | Darker, still on-palette. Text contrast ~15:1 |
| `brightBlack` | `#585B70` (Surface2) | `#6C7086` (Overlay0) | Dim/secondary text (Claude Code hints, comments, inactive tmux) was too dark to read |
| `brightWhite` | `#A6ADC8` (Subtext0) | `#CDD6F4` (Text) | Upstream scheme has bright*darker* than normal white — inverted; fixed |
| bright red/green/blue/yellow/cyan/purple | same as normal | lightened ~8% | Bright variants were literal duplicates, so bold/intense text carried no signal |
| tab row | `#181825` / `#11111B` | `#0B0B11` / `#07070B` | Chrome recedes below the content |

Readability/rendering settings on the WSL profile:

| Setting | Value | Effect |
|---|---|---|
| `opacity` + `useAcrylic` | `92` + `true` | Subtle transparency. Acrylic **blurs** what's behind, so it stays readable — plain transparency at the same value does not |
| `unfocusedAppearance.opacity` | `86` | Inactive split panes recede |
| `font.cellHeight` | `1.25` | Extra line spacing for dense code |
| `intenseTextStyle` | `all` | Bold text renders bold *and* bright |
| `adjustIndistinguishableColors` | `never` | WT does not "helpfully" recolor and break palette fidelity |
| `antialiasingMode` | `grayscale` | No ClearType color fringing on a near-black background |
| `padding` | `10, 6` | Breathing room at the edges |

> **Revert:** restore `LocalState/settings.json.bak-pre-mocha-deep`, or just
> pick `Catppuccin Mocha` under Appearance in the WT settings UI.

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

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

- Windows Terminal: `Catppuccin Mocha Black` color scheme + window/tab theme
  (both embedded in settings.json; derived from catppuccin/windows-terminal)
- tmux: `catppuccin/tmux#v2.1.3` via TPM (`prefix + I` to install)
- Neovim: `catppuccin/nvim` (flavour mocha) in `nvim/.config/nvim`, the config
  `~/.config/nvim` symlinks to. The dormant `~/wsl-dotfiles/nvim` copy is still
  on LazyVim's default tokyonight; it is not symlinked anywhere and was last
  touched 2025-08-26.

Three scheme + theme pairs ship in settings.json — `Catppuccin Mocha Black`
(active), `Catppuccin Mocha Deep`, and stock `Catppuccin Mocha`. Any of them
can be picked from the WT settings UI under Appearance.

### Catppuccin Mocha Black (2026-08-17)

Neutral black ground, Catppuccin ink. Every Catppuccin surface colour carries
a blue-violet tint — Crust `#11111B` is `R17 G17 B27`, so blue sits ten points
above the others and the "black" reads faintly purple. This variant drops the
ground to a true neutral and leaves the text palette alone.

| Change | From | To | Why |
|---|---|---|---|
| `background` | `#11111B` (Crust) | `#000000` | True neutral, no hue. Text contrast ~17:1 |
| `black` (ANSI 0) | `#45475A` (Surface1) | `#3A3A3A` | Was blue-tinted; now neutral grey |
| `selectionBackground` | `#45475A` | `#3A3A3A` | Same reason |
| `opacity` + `useAcrylic` | `92` + `true` | `100` + `false` | Acrylic blur mixes desktop colour into the ground, so black was never actually black |
| `unfocusedAppearance` | `opacity: 86` | `background: #0C0C0C` | See below |
| tab row | `#0B0B11` / `#07070B` | `#0C0C0C` / `#060606` | Chrome follows the ground to neutral |

All sixteen palette colours (red, green, blue, the brights) are unchanged from
Mocha Deep. Only the ground and the two grey surfaces moved.

**Why `unfocusedAppearance` had to change.** It used to lean on `opacity: 86`,
which reads as *acrylic* blur only while `useAcrylic` is true. With acrylic off,
the same value becomes plain unblurred transparency, and the desktop shows
through hard. Dimming the background further is not an option either — the
ground is already `#000000`. So the relationship inverts: the focused pane is
the deepest black, and unfocused panes lift slightly to `#0C0C0C`.

### Catppuccin Mocha Deep (2026-07-27)

A darker, higher-contrast variant tuned for code + Claude Code. Superseded as
the active scheme on 2026-08-17, kept selectable.

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
| `opacity` + `useAcrylic` | `100` + `false` | Fully opaque. Set opacity below 100 with acrylic **on** for blurred transparency; with acrylic **off** you get plain transparency, which is much harder to read against |
| `unfocusedAppearance.background` | `#0C0C0C` | Inactive split panes lift off the black |
| `font.cellHeight` | `1.25` | Extra line spacing for dense code |
| `intenseTextStyle` | `all` | Bold text renders bold *and* bright |
| `adjustIndistinguishableColors` | `never` | WT does not "helpfully" recolor and break palette fidelity |
| `antialiasingMode` | `grayscale` | No ClearType color fringing on a near-black background |
| `padding` | `10, 6` | Breathing room at the edges |

> **Revert:** pick another scheme under Appearance in the WT settings UI, or
> restore a backup from `LocalState/` — `settings.json.bak-pre-black` (before
> the neutral ground), `settings.json.bak-pre-maple` (before the font change),
> `settings.json.bak-pre-mocha-deep` (before the Deep variant).
>
> The scheme and the window theme are separate keys. Changing the scheme in the
> UI leaves the tab row on the old colour, so set the top-level `"theme"` to the
> matching name too.

## Fonts

**Maple Mono NF** v7.9, single face, applied 2026-08-17.

One font draws both text and icons, so no fallback list is needed. It has
ligatures (`liga` + `calt`) and Nerd Font glyphs built in, and `fc-query`
reports `spacing=100` (strict monospace) — icons occupy exactly one cell,
which is what keeps the tmux status bar and the Claude Code TUI aligned.

```json
"face": "Maple Mono NF",
"features": { "calt": 1, "liga": 1 }
```

`features` pins the OpenType ligature tables on rather than relying on the
renderer's default. Windows Terminal has supported `font.features` since 1.16.

### Picking the release asset

The maple-font release page carries ~60 assets whose names encode variants.
Decode before downloading:

| Marker | Meaning |
|---|---|
| `NL` | **N**o **L**igatures — avoid |
| `NF` | Nerd Font glyphs included — want |
| `CN` | Chinese subset, ~150 MB — skip |
| `Normal` | Tamed letterforms (plainer `@`, `l`, `f`) |
| `unhinted` | No hinting; hinted renders better on Windows at 13px |

So the wanted asset is `MapleMono-NF.zip` (~20 MB). Checksums are published
alongside as `MapleMono-NF.sha256` — verify before installing.

### Installing per-user from WSL

Fonts go in `%LOCALAPPDATA%\Microsoft\Windows\Fonts` **and** need a registry
entry, or Windows will not see them. The value name must be
`<Family> <Style> (TrueType)` and the data the full Windows path.

```sh
KEY="HKCU\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Fonts"
for f in MapleMono-NF-*.ttf; do
  fam=$(fc-query -f '%{family}' "$f" | cut -d, -f1)
  sty=$(fc-query -f '%{style}'  "$f" | cut -d, -f1)
  cp -f "$f" "/mnt/c/Users/yanni/AppData/Local/Microsoft/Windows/Fonts/$f"
  reg.exe add "$KEY" /v "$fam $sty (TrueType)" /t REG_SZ \
    /d "C:\\Users\\yanni\\AppData\\Local\\Microsoft\\Windows\\Fonts\\$f" /f </dev/null
done
```

Two traps, both hit while doing this:

- `fc-query` returns **two** comma-joined values for any weight outside
  Regular/Italic/Bold/BoldItalic — the typographic name and the legacy one.
  Registering the raw string produces junk like
  `Maple Mono NF,Maple Mono NF Light Light,Regular`. `cut -d, -f1` takes the
  typographic name, matching how JetBrainsMono NFM is registered.
- `reg.exe` reads stdin, so inside a loop it swallows the remaining input and
  the loop runs once. Redirect with `</dev/null`.

### Previously

CommitMono for text with JetBrainsMono NFM as a per-glyph fallback
(`"face": "CommitMono, JetBrainsMono NFM"`). It worked, but CommitMono has no
Nerd Font glyphs, so every icon was drawn by a second typeface. Both fonts are
still installed and can be restored by putting that comma list back, or by
restoring `LocalState/settings.json.bak-pre-maple`.

Also still installed and ligature-capable: FiraCode NFM (widest ligature set),
VictorMono NF (cursive italics), IntoneMono NF, Iosevka NF (`calt` only, no
`liga` table).

## Paste redundancy (ported from the wezterm fix)

Three paste triggers so a single shadowed hotkey can never lock you out
again: `Ctrl+V` / `Ctrl+Shift+V`, `Shift+Insert`, and right-click
(WT default mouse behavior).

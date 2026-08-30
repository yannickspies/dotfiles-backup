-- WezTerm config for the WSL2 stack: WezTerm (Windows, nightly) → Ubuntu-24.04 → tmux.
-- Canonical copy: ~/dotfiles/windows/wezterm/wezterm.lua. apply.sh installs it to
-- %USERPROFILE%\.wezterm.lua and wezterm-watch.service re-copies it on every save,
-- which is what makes WezTerm hot-reload (it watches the local file, and change
-- notifications never arrive over \\wsl.localhost — microsoft/WSL#7674).
--
-- Mirrors the Windows Terminal profile "yspies-dotfiles-ubuntu": Catppuccin Mocha
-- Neutral, Maple Mono NF 13, cell height 1.25, padding 10/6, bar cursor.
--
-- Trial started 2026-08-29. Retired in 2025 because Ctrl+Shift+V pasted nothing into
-- WSL (wezterm#5368, closed by its reporter, never fixed). Run the day-one paste test
-- in ../README.md before trusting it.

local wezterm = require("wezterm")
local act = wezterm.action
local config = wezterm.config_builder()

local DISTRO = "Ubuntu-24.04"

-- === Shell: a WSL domain, not `wsl.exe` as a program ===
-- A domain gives new tabs and splits the distro's home/cwd semantics.
local wsl_domains = wezterm.default_wsl_domains()
for _, dom in ipairs(wsl_domains) do
	dom.default_cwd = "~"
end
config.wsl_domains = wsl_domains
config.default_domain = "WSL:" .. DISTRO

-- === Font ===
-- Maple Mono NF draws text and Nerd Font glyphs from one strict-monospace face, so no
-- fallback list. calt/liga are WezTerm's defaults; pinned to match the WT profile.
config.font = wezterm.font("Maple Mono NF")
config.font_size = 14.0
config.harfbuzz_features = { "calt=1", "liga=1" }
config.line_height = 1
config.bold_brightens_ansi_colors = "BrightAndBold" -- WT intenseTextStyle = all
config.warn_about_missing_glyphs = false

-- === Colors: Catppuccin Mocha Neutral (palette documented in ../README.md) ===
config.colors = {
	foreground = "#CDD6F4",
	background = "#121212",
	cursor_bg = "#F5E0DC",
	cursor_fg = "#121212",
	cursor_border = "#F5E0DC",
	selection_bg = "#3A3A3A",
	selection_fg = "none",
	ansi = { "#3A3A3A", "#F38BA8", "#A6E3A1", "#F9E2AF", "#89B4FA", "#CBA6F7", "#94E2D5", "#BAC2DE" },
	brights = { "#6C7086", "#F5A0B8", "#B5E8B0", "#FAE8BE", "#A5C8FB", "#D5B8F8", "#A6E9DD", "#CDD6F4" },
	tab_bar = {
		background = "#0C0C0C",
		active_tab = { bg_color = "#121212", fg_color = "#CDD6F4" },
		inactive_tab = { bg_color = "#0C0C0C", fg_color = "#6C7086" },
		inactive_tab_hover = { bg_color = "#121212", fg_color = "#BAC2DE" },
		new_tab = { bg_color = "#0C0C0C", fg_color = "#6C7086" },
		new_tab_hover = { bg_color = "#121212", fg_color = "#CDD6F4" },
	},
}
config.window_background_opacity = 1.0
-- WT dims unfocused panes to #0C0C0C on a #121212 ground, about 0.67 brightness.
config.inactive_pane_hsb = { saturation = 1.0, brightness = 0.7 }

-- === Window ===
config.window_decorations = "TITLE | RESIZE"
config.window_padding = { left = 10, right = 10, top = 6, bottom = 6 }
config.enable_tab_bar = true
config.use_fancy_tab_bar = true
config.window_frame = {
	active_titlebar_bg = "#0C0C0C",
	inactive_titlebar_bg = "#080808",
	font = wezterm.font("Maple Mono NF"),
	font_size = 10.0,
}
config.show_tab_index_in_tab_bar = false
config.adjust_window_size_when_changing_font_size = false
config.window_close_confirmation = "NeverPrompt"
config.default_cursor_style = "SteadyBar"
config.audible_bell = "Disabled"
config.scrollback_lines = 10000 -- tmux keeps its own history

-- === Rendering ===
-- OpenGL rather than WebGpu: WebGpu aborts on config reload in long-lived windows
-- (wezterm#7981, nightly 20260716) and the watcher triggers a reload on every save.
config.front_end = "OpenGL"
config.max_fps = 120
config.animation_fps = 60

-- === Keyboard ===
-- Keep the kitty keyboard protocol OFF. On Win11 it makes every Shift+<char> emit
-- garbage (wezterm#6900, reconfirmed 2026-08-15). Claude Code enables Shift+Enter from
-- TERM_PROGRAM=WezTerm instead, which WezTerm pushes into WSL through WSLENV.
config.enable_kitty_keyboard = false

-- Ctrl+C copies when there is a selection and sends ^C otherwise, matching the
-- Windows Terminal `copy` action bound to ctrl+c.
local function copy_or_interrupt(window, pane)
	local sel = window:get_selection_text_for_pane(pane)
	if sel ~= nil and sel ~= "" then
		window:perform_action(act.CopyTo("Clipboard"), pane)
		window:perform_action(act.ClearSelection, pane)
	else
		window:perform_action(act.SendKey({ key = "c", mods = "CTRL" }), pane)
	end
end

-- Split along the longer axis, like Windows Terminal's `split: auto`.
local function split_auto(window, pane)
	local dims = pane:get_dimensions()
	local direction = (dims.cols > dims.viewport_rows * 2.2) and "Right" or "Down"
	window:perform_action(act.SplitPane({ direction = direction }), pane)
end

config.keys = {
	-- Paste: three triggers so one shadowed hotkey can never lock paste out again.
	{ key = "v", mods = "CTRL", action = act.PasteFrom("Clipboard") },
	{ key = "v", mods = "CTRL|SHIFT", action = act.PasteFrom("Clipboard") },
	{ key = "Insert", mods = "SHIFT", action = act.PasteFrom("Clipboard") },
	-- Copy
	{ key = "c", mods = "CTRL", action = wezterm.action_callback(copy_or_interrupt) },
	{ key = "c", mods = "CTRL|SHIFT", action = act.CopyTo("Clipboard") },
	-- Find and split, same chords as the Windows Terminal profile.
	{ key = "f", mods = "CTRL|SHIFT", action = act.Search({ CaseInSensitiveString = "" }) },
	{ key = "d", mods = "ALT|SHIFT", action = wezterm.action_callback(split_auto) },
}

config.mouse_bindings = {
	-- Right-click pastes without the keyboard. mouse_reporting = true is required:
	-- tmux runs `mouse on`, and without it WezTerm forwards the click to tmux instead.
	{
		event = { Up = { streak = 1, button = "Right" } },
		mods = "NONE",
		mouse_reporting = true,
		action = act.PasteFrom("Clipboard"),
	},
}

return config

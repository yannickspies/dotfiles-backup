# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a personal dotfiles repository with configurations for:
- **Neovim** (`nvim/`) - LazyVim-based configuration
- **Tmux** (`tmux/`) - Terminal multiplexer configuration

The repository uses a stow-compatible structure where config files are nested in directories that mirror their target locations (e.g., `nvim/.config/nvim/` maps to `~/.config/nvim/`).

## Key Commands

### Neovim Development

When working with the Neovim configuration:
- Plugin configurations go in `nvim/.config/nvim/lua/plugins/`
- Core settings are in `nvim/.config/nvim/lua/config/`
- LazyVim extras are configured in `nvim/.config/nvim/lua/config/lazy.lua`

To test changes:
```bash
# Launch Neovim from the config directory
cd nvim/.config/nvim && nvim

# Or use NVIM_APPNAME to test without affecting main config
NVIM_APPNAME=nvim-test nvim
```

### Installing/Deploying Configs

Currently manual installation is required. Common approaches:
```bash
# Using GNU Stow (if available)
stow nvim
stow tmux

# Or manual symlinking
ln -sf ~/dotfiles/nvim/.config/nvim ~/.config/nvim
ln -sf ~/dotfiles/tmux/.tmux.conf ~/.tmux.conf
```

## Architecture

### Neovim Configuration
- Built on **LazyVim** distribution for modern IDE-like features
- Uses `lazy.nvim` for plugin management with automatic lazy loading
- Language support via LSP servers managed by Mason
- Configured languages: TypeScript/JavaScript, Angular, Python, SQL, Markdown, Tailwind CSS
- ESLint integration for JavaScript/TypeScript linting

### Tmux Configuration
- Minimal setup with TPM (Tmux Plugin Manager)
- Mouse support and true color enabled
- Optimized escape time for Neovim integration

## Important Notes

- The `nvim` directory contains its own git repository (shown in git status)
- Plugin versions are locked in `nvim/.config/nvim/lazy-lock.json`
- No automated setup scripts exist - installation is manual
- LazyVim provides most functionality out-of-the-box with minimal customization needed
-- Options are automatically loaded before lazy.nvim startup
-- Default options that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/options.lua
-- Add any additional options here

-- Pin the swappable defaults explicitly (independent of install generation)
vim.g.lazyvim_picker = "snacks"
vim.g.lazyvim_cmp = "blink.cmp"
vim.g.lazyvim_explorer = "snacks"

-- Indentation: 4 spaces (matches the websites monorepo .editorconfig/.prettierrc)
vim.opt.tabstop = 4
vim.opt.shiftwidth = 4
vim.opt.softtabstop = 4
vim.opt.expandtab = true

vim.opt.colorcolumn = "100"
vim.opt.scrolloff = 10
vim.opt.hlsearch = false
vim.opt.swapfile = false

-- Keep pre-migration undo history
vim.opt.undofile = true
vim.opt.undodir = vim.fn.expand("~/.vim/undodir")

vim.opt.iskeyword:append("-")

-- Websites-monorepo file types. Registered here (not autocmds.lua) so detection
-- is in place before buffers passed on the command line are loaded.
vim.filetype.add({
  extension = {
    xlf = "xml", -- Angular XLIFF translations
    njk = "jinja", -- Eleventy Nunjucks; jinja grammar is close enough
  },
  pattern = {
    -- core's htmlangular heuristic misses simple templates; make it deterministic
    [".*%.component%.html"] = "htmlangular",
  },
})

-- WSL clipboard bridge: route the system clipboard through win32yank instead of
-- letting Neovim auto-pick xsel (which talks to the flaky WSLg X bridge). win32yank
-- is UTF-8 clean and bidirectional, so yank-out and "+p paste-in both work.
if vim.fn.has("wsl") == 1 and vim.fn.executable("win32yank.exe") == 1 then
  vim.g.clipboard = {
    name = "win32yank",
    copy = {
      ["+"] = "win32yank.exe -i --crlf",
      ["*"] = "win32yank.exe -i --crlf",
    },
    paste = {
      ["+"] = "win32yank.exe -o --lf",
      ["*"] = "win32yank.exe -o --lf",
    },
    cache_enabled = 0,
  }
end

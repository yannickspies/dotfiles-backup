-- Keymaps are automatically loaded on the VeryLazy event
-- Default keymaps that are always set: https://github.com/LazyVim/LazyVim/blob/main/lua/lazyvim/config/keymaps.lua
-- Add any additional keymaps here

-- Keep the cursor centered when half-page scrolling
vim.keymap.set("n", "<C-d>", "<C-d>zz", { desc = "Half page down (centered)" })
vim.keymap.set("n", "<C-u>", "<C-u>zz", { desc = "Half page up (centered)" })

-- Copilot accept on <C-j> (muscle memory from copilot.vim; Tab via blink also works).
-- No-op when the suggestion module is inactive (e.g. vim.g.ai_cmp routing).
vim.keymap.set("i", "<C-j>", function()
  local ok, suggestion = pcall(require, "copilot.suggestion")
  if ok and suggestion.is_visible() then
    suggestion.accept()
  end
end, { desc = "Accept Copilot suggestion" })

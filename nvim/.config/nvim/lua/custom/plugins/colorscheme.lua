-- Catppuccin - Colorscheme
-- https://github.com/catppuccin/nvim

return {
  'catppuccin/nvim',
  name = 'catppuccin',
  priority = 1000, -- Make sure to load this before all the other start plugins.
  config = function()
    require('catppuccin').setup {
      flavour = 'mocha', -- Set to Mocha variant (latte, frappe, macchiato, mocha)
      transparent_background = true, -- Enable transparency to match terminal opacity
      styles = {
        comments = {}, -- No special styling for comments (removes italics)
      },
      background = {
        light = 'latte',
        dark = 'mocha',
      },
    }
    -- Load the Catppuccin colorscheme
    vim.cmd.colorscheme 'catppuccin'
  end,
}
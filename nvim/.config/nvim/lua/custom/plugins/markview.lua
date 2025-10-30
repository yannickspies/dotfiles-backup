-- Markview.nvim - Highly customizable markdown, LaTeX, and Typst previewer
-- https://github.com/OXY2DEV/markview.nvim

return {
  'OXY2DEV/markview.nvim',
  lazy = false, -- Recommended to prevent lazy-loading for proper initialization
  dependencies = {
    'nvim-treesitter/nvim-treesitter',
  },
  opts = {
    -- Enable for markdown and HTML files
    filetypes = { 'markdown', 'html' },
    modes = { 'n', 'no', 'c' }, -- Preview in normal, operator-pending, and command modes
    -- Use default settings for all other options
  },
}

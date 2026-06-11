-- Catppuccin Mocha — matches Windows Terminal scheme and tmux plugin.
return {
  {
    'catppuccin/nvim',
    name = 'catppuccin',
    priority = 1000, -- load before other start plugins so highlights apply early
    config = function()
      require('catppuccin').setup {
        flavour = 'mocha',
      }
      vim.cmd.colorscheme 'catppuccin'
    end,
  },
}

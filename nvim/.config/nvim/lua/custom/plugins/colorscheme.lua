return {
  '0xstepit/flow.nvim',
  lazy = false,
  priority = 1000,
  opts = {
    theme = {
      style = 'dark',
      contrast = 'default',
      transparent = false,
    },
    colors = {
      mode = 'default',
      fluo = 'pink',
    },
    ui = {
      borders = 'theme',
      aggressive_spell = false,
    },
  },
  config = function(_, opts)
    require('flow').setup(opts)
    vim.cmd.colorscheme 'flow'
  end,
}

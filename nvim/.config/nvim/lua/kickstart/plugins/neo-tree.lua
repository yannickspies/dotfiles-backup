-- Neo-tree is a Neovim plugin to browse the file system
-- https://github.com/nvim-neo-tree/neo-tree.nvim

return {
  'nvim-neo-tree/neo-tree.nvim',
  version = '*',
  dependencies = {
    'nvim-lua/plenary.nvim',
    'nvim-tree/nvim-web-devicons', -- not strictly required, but recommended
    'MunifTanjim/nui.nvim',
  },
  lazy = false,
  keys = {
    { '\\', ':Neotree reveal<CR>', desc = 'NeoTree reveal', silent = true },
  },
  opts = {
    filesystem = {
      filtered_items = {
        visible = true, -- Show hidden files by default
        hide_dotfiles = false, -- Don't hide dotfiles
        hide_gitignored = false, -- Optionally show gitignored files
        hide_by_name = {
          '.git', -- Still hide .git folder as it's usually not needed
        },
      },
      window = {
        mappings = {
          ['\\'] = 'close_window',
          ['H'] = 'toggle_hidden', -- Add toggle for hidden files
        },
      },
    },
  },
}

-- Snacks.nvim - A collection of small QoL plugins for Neovim
-- https://github.com/folke/snacks.nvim

return {
  'folke/snacks.nvim',
  priority = 1000,
  lazy = false,
  opts = {
    -- Enable specific features
    bigfile = { enabled = true }, -- Better performance for large files
    notifier = { enabled = true }, -- Pretty notifications (replaces fidget.nvim)
    quickfile = { enabled = true }, -- Faster file loading
    statuscolumn = { enabled = false }, -- We're using default for now
    words = { enabled = true }, -- Enhanced LSP reference highlighting

    -- Smooth scrolling animations
    scroll = {
      enabled = true,
      animate = {
        duration = { step = 15, total = 150 },
        easing = 'linear',
      },
    },

    -- Better buffer deletion
    bufdelete = {
      enabled = true,
    },

    -- Smart file renaming with LSP integration
    rename = {
      enabled = true,
    },

    -- Configure notifier (replaces fidget.nvim)
    notifier_opts = {
      timeout = 3000,
      width = { min = 40, max = 0.4 },
      height = { min = 1, max = 0.6 },
      margin = { top = 0, right = 1, bottom = 0 },
      icons = {
        error = "󰅚 ",
        warn = "󰀪 ",
        info = "󰋽 ",
        debug = "󰠭 ",
        trace = "󰏫 ",
      },
    },
  },
  keys = {
    -- Notification history
    { '<leader>sn', function() require('snacks').notifier.show_history() end, desc = 'Show notification history' },

    -- Buffer deletion
    { '<leader>bd', function() require('snacks').bufdelete.delete() end, desc = 'Delete buffer' },
    { '<leader>bo', function() require('snacks').bufdelete.other() end, desc = 'Delete other buffers' },

    -- Smart rename
    { '<leader>rn', function() require('snacks').rename.rename_file() end, desc = 'Rename file' },

    -- Dismiss notifications
    { '<leader>nd', function() require('snacks').notifier.hide() end, desc = 'Dismiss all notifications' },
  },
  init = function()
    -- Override vim.notify with snacks notifier
    vim.notify = function(msg, level, opts)
      require('snacks').notifier.notify(msg, level, opts)
    end
  end,
}
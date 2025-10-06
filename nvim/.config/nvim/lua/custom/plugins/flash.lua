-- Flash.nvim - Navigate your code with search labels and Treesitter integration
-- https://github.com/folke/flash.nvim

return {
  'folke/flash.nvim',
  event = 'VeryLazy',
  opts = {
    -- Configure flash.nvim behavior
    modes = {
      -- Customize search mode
      search = {
        enabled = true,
        highlight = { backdrop = false },
      },
      -- Customize character mode
      char = {
        enabled = true,
        jump_labels = true,
      },
    },
    -- Treesitter mode configuration
    treesitter = {
      labels = 'abcdefghijklmnopqrstuvwxyz',
      jump = { pos = 'range', autojump = true },
      search = { incremental = false },
      label = { before = true, after = true, style = 'inline' },
      highlight = {
        backdrop = false,
        matches = false,
      },
    },
    -- Label configuration
    label = {
      uppercase = false,
      rainbow = {
        enabled = false,
      },
    },
    -- Highlight configuration
    highlight = {
      backdrop = true,
      matches = false,
      priority = 5000,
      groups = {
        match = 'FlashMatch',
        current = 'FlashCurrent',
        backdrop = 'FlashBackdrop',
        label = 'FlashLabel',
      },
    },
    -- Action configuration
    action = nil,
    -- Pattern configuration
    pattern = '',
    -- Continue last search
    continue = false,
    -- Prompt configuration
    prompt = {
      enabled = true,
      prefix = { { '⚡', 'FlashPromptIcon' } },
    },
  },
  keys = {
    {
      's',
      mode = { 'n', 'x', 'o' },
      function()
        require('flash').jump()
      end,
      desc = 'Flash',
    },
    {
      'S',
      mode = { 'n', 'x', 'o' },
      function()
        require('flash').treesitter()
      end,
      desc = 'Flash Treesitter',
    },
    {
      'r',
      mode = 'o',
      function()
        require('flash').remote()
      end,
      desc = 'Remote Flash',
    },
    {
      'R',
      mode = { 'o', 'x' },
      function()
        require('flash').treesitter_search()
      end,
      desc = 'Treesitter Search',
    },
    {
      '<c-s>',
      mode = { 'c' },
      function()
        require('flash').toggle()
      end,
      desc = 'Toggle Flash Search',
    },
  },
}
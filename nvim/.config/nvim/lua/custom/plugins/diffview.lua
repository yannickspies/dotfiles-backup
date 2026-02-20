return {
  'sindrets/diffview.nvim',
  cmd = { 'DiffviewOpen', 'DiffviewFileHistory', 'DiffviewClose' },
  keys = {
    { '<leader>gd', '<cmd>DiffviewOpen<cr>', desc = 'Diffview: open' },
    { '<leader>gh', '<cmd>DiffviewFileHistory %<cr>', desc = 'Diffview: file history' },
    { '<leader>gH', '<cmd>DiffviewFileHistory<cr>', desc = 'Diffview: branch history' },
  },
  opts = {},
}

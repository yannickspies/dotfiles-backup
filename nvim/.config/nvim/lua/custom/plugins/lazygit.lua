return {
  'kdheepak/lazygit.nvim',
  lazy = false,
  cmd = {
    'LazyGit',
    'LazyGitConfig',
    'LazyGitCurrentFile',
    'LazyGitFilter',
    'LazyGitFilterCurrentFile',
  },
  dependencies = {
    'nvim-lua/plenary.nvim',
  },
  keys = {
    { '<leader>lg', '<cmd>LazyGit<cr>', desc = 'LazyGit' },
    { '<leader>gc', '<cmd>LazyGitConfig<cr>', desc = 'LazyGit Config' },
    { '<leader>gf', '<cmd>LazyGitCurrentFile<cr>', desc = 'LazyGit Current File' },
  },
  config = function()
    vim.g.lazygit_floating_window_winblend = 0
    vim.g.lazygit_floating_window_scaling_factor = 0.9
    vim.g.lazygit_floating_window_border_chars = { '╭', '─', '╮', '│', '╯', '─', '╰', '│' }
    vim.g.lazygit_use_neovim_remote = 1
  end,
}
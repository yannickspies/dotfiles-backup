return {
  'stevearc/oil.nvim',
  dependencies = { 'nvim-tree/nvim-web-devicons' },
  lazy = false,
  config = function()
    require('oil').setup {
      view_options = {
        show_hidden = true,
      },
      delete_to_trash = true,
      skip_confirm_for_simple_edits = true,
    }
    vim.keymap.set('n', '-', '<CMD>Oil<CR>', { desc = 'Open parent directory' })
  end,
}

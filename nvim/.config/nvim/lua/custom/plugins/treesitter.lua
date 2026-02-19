-- Treesitter - Highlight, edit, and navigate code
-- https://github.com/nvim-treesitter/nvim-treesitter

return {
  'nvim-treesitter/nvim-treesitter',
  branch = 'main',
  lazy = false,
  build = ':TSUpdate',
  config = function()
    ---@diagnostic disable-next-line: missing-fields
    require('nvim-treesitter.configs').setup {
      ensure_installed = {
        'bash', 'c', 'diff', 'html', 'lua', 'luadoc',
        'markdown', 'markdown_inline', 'python', 'query', 'vim', 'vimdoc',
      },
      highlight = {
        enable = true,
        additional_vim_regex_highlighting = { 'ruby' },
      },
      indent = {
        enable = true,
        disable = { 'ruby' },
      },
    }
  end,
}

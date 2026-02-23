-- Treesitter - Highlight, edit, and navigate code
-- https://github.com/nvim-treesitter/nvim-treesitter

return {
  'nvim-treesitter/nvim-treesitter',
  branch = 'main',
  lazy = false,
  build = ':TSUpdate',
  config = function()
    require('nvim-treesitter').setup()

    -- Install parsers
    local parsers = {
      'bash', 'c', 'diff', 'html', 'lua', 'luadoc',
      'markdown', 'markdown_inline', 'python', 'query', 'vim', 'vimdoc',
    }

    -- Ensure parsers are installed
    vim.api.nvim_create_autocmd('User', {
      pattern = 'LazyDone',
      once = true,
      callback = function()
        local installed = require('nvim-treesitter').installed()
        for _, lang in ipairs(parsers) do
          if not vim.tbl_contains(installed, lang) then
            vim.cmd('TSInstall ' .. lang)
          end
        end
      end,
    })
  end,
}

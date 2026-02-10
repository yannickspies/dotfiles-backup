return {
  'CopilotC-Nvim/CopilotChat.nvim',
  dependencies = {
    { 'github/copilot.vim' },
    { 'nvim-lua/plenary.nvim' },
  },
  build = 'make tiktoken',
  cmd = { 'CopilotChat', 'CopilotChatOpen', 'CopilotChatToggle' },
  keys = {
    { '<leader>cc', ':CopilotChatToggle<CR>', desc = 'Copilot Chat Toggle' },
    { '<leader>ce', ':CopilotChatExplain<CR>', mode = 'v', desc = 'Copilot Explain Selection' },
    { '<leader>ca', ':CopilotChat ', desc = 'Copilot Chat Ask' },
    {
      '<leader>cq',
      function()
        local input = vim.fn.input 'Copilot Chat: '
        if input ~= '' then
          require('CopilotChat').ask(input, { selection = require('CopilotChat.select').buffer })
        end
      end,
      desc = 'Copilot Chat (whole buffer)',
    },
  },
  opts = {
    selection = function(source)
      local select = require 'CopilotChat.select'
      return select.visual(source) or select.buffer(source)
    end,
    window = {
      layout = 'vertical',
      width = 0.35,
    },
  },
}

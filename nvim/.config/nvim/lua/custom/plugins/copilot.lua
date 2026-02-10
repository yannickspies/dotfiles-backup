return {
  'github/copilot.vim',
  event = 'InsertEnter',
  cmd = 'Copilot',
  config = function()
    -- Accept suggestion with Ctrl+J (Tab conflicts with other plugins)
    vim.g.copilot_assume_mapped = true
    vim.keymap.set('i', '<C-j>', 'copilot#Accept("\\<CR>")', { expr = true, replace_keycodes = false, desc = 'Copilot Accept' })
    vim.keymap.set('i', '<C-l>', '<Plug>(copilot-accept-word)', { desc = 'Copilot Accept Word' })
    vim.keymap.set('i', '<C-]>', '<Plug>(copilot-next)', { desc = 'Copilot Next Suggestion' })
    vim.keymap.set('i', '<M-[>', '<Plug>(copilot-previous)', { desc = 'Copilot Previous Suggestion' })
    vim.keymap.set('i', '<C-\\>', '<Plug>(copilot-dismiss)', { desc = 'Copilot Dismiss' })

    -- Disable default Tab mapping to avoid conflicts with blink.cmp
    vim.g.copilot_no_tab_map = true
  end,
}

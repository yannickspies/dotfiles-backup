-- Moved from <leader>gd/gh/gH to the <leader>gv group: LazyVim already binds
-- <leader>gd and gitsigns hunk maps in that range.
return {
  "sindrets/diffview.nvim",
  cmd = { "DiffviewOpen", "DiffviewFileHistory", "DiffviewClose" },
  keys = {
    { "<leader>gvo", "<cmd>DiffviewOpen<cr>", desc = "Diffview: open" },
    { "<leader>gvf", "<cmd>DiffviewFileHistory %<cr>", desc = "Diffview: file history" },
    { "<leader>gvb", "<cmd>DiffviewFileHistory<cr>", desc = "Diffview: branch history" },
    { "<leader>gvq", "<cmd>DiffviewClose<cr>", desc = "Diffview: close" },
  },
  opts = {},
}

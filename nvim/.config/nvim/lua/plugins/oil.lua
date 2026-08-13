return {
  "stevearc/oil.nvim",
  -- must load at startup so `nvim <dir>` and netrw-style entry points open Oil
  lazy = false,
  opts = {
    default_file_explorer = true,
    view_options = {
      show_hidden = true,
    },
    delete_to_trash = true,
    skip_confirm_for_simple_edits = true,
  },
  keys = {
    { "-", "<CMD>Oil<CR>", desc = "Open parent directory (Oil)" },
    { "\\", "<CMD>Oil<CR>", desc = "Open file explorer (Oil)" },
  },
}

-- Tweaks for the InShared websites monorepo (~/projects/frontend/websites):
-- Nunjucks templates, and 32 git worktrees that would pollute picker results.
return {
  {
    "nvim-treesitter/nvim-treesitter",
    opts = { ensure_installed = { "jinja" } },
  },

  -- Format .njk through prettier; the repo's .prettierrc maps *.njk to the
  -- jinja-template plugin, and conform resolves the repo-local prettier binary.
  {
    "stevearc/conform.nvim",
    opts = {
      formatters_by_ft = {
        jinja = { "prettier" },
      },
    },
  },

  {
    "folke/snacks.nvim",
    opts = {
      picker = {
        sources = {
          files = { exclude = { ".worktrees" } },
          grep = { exclude = { ".worktrees" } },
        },
      },
    },
  },
}

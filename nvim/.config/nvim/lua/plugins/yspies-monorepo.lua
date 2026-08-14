-- Tweaks for the personal yspies Nx monorepo (~/projects/personal/yspies-monorepo).
--
-- Stack the LazyVim extras do not cover on their own:
--   Angular 21 + NestJS 11 on Nx 22 / pnpm  -> lang.typescript + lang.angular extras
--   LESS (232 files, no SCSS)               -> cssls + prettier, wired below
--   Python 3.12 under uv (libs/shared/*)    -> lang.python extra
--   Drizzle SQL migrations, TOML, XML       -> treesitter grammars below
--
-- Gated on the checkout being present so the work laptop does not pay for any
-- of it.
local host = require("config.host")

if not host.is_personal then
  return {}
end

return {
  {
    "nvim-treesitter/nvim-treesitter",
    opts = {
      -- No `less` grammar exists upstream; Neovim's bundled syntax/less.vim
      -- handles highlighting and cssls below does the semantic work.
      ensure_installed = {
        "sql", -- libs/shared/db drizzle migrations
        "xml", -- angular.json siblings, GitHub workflow XML, XLIFF
        "embedded_template", -- tools/workspace-plugin generator *.template files
      },
    },
  },

  -- LESS is the styling language across every app here (PrimeNG + @primeuix
  -- themes, no Tailwind). cssls covers less/scss/css: completion for custom
  -- properties, go-to-definition on imports, unknown-at-rule diagnostics.
  {
    "neovim/nvim-lspconfig",
    opts = {
      servers = {
        cssls = {
          settings = {
            -- PrimeUIX themes and the design tokens use at-rules and unknown
            -- properties cssls does not ship a schema for; downgrade the noise
            -- rather than train yourself to ignore diagnostics.
            less = { validate = true, lint = { unknownAtRules = "ignore" } },
            scss = { validate = true, lint = { unknownAtRules = "ignore" } },
            css = { validate = true, lint = { unknownAtRules = "ignore" } },
          },
        },
        -- Emmet abbreviations in Angular templates and LESS blocks.
        emmet_ls = {
          filetypes = { "css", "less", "scss", "html", "htmlangular" },
          init_options = {
            html = { options = { ["bem.enabled"] = true } },
          },
        },
      },
    },
  },

  -- Root .prettierrc is `{ "singleQuote": true }`; conform resolves the
  -- repo-local prettier so .less goes through the same formatter as CI.
  {
    "stevearc/conform.nvim",
    opts = {
      formatters_by_ft = {
        less = { "prettier" },
      },
    },
  },

  -- Both worktree roots hold full duplicate checkouts. They are gitignored, so
  -- the default picker already skips them — these excludes keep hidden/ignored
  -- searches (<leader>fF, "ignored" toggles) usable too.
  {
    "folke/snacks.nvim",
    opts = {
      picker = {
        sources = {
          files = { exclude = { ".worktrees", ".claude/worktrees", "dist", ".nx", "coverage" } },
          grep = { exclude = { ".worktrees", ".claude/worktrees", "dist", ".nx", "coverage" } },
        },
      },
    },
  },
}

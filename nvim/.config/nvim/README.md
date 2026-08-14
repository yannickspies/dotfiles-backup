# Neovim config

LazyVim, shared by two machines, branching on which project checkout it finds.
`lua/config/host.lua` probes for the InShared `websites` monorepo and the
personal `yspies-monorepo`; every machine-specific plugin file returns `{}` when
its checkout is absent. Detection is by path, not hostname — hostnames change on
reimage and on WSL distro renames.

## Files

| File | Holds | Applies to |
|---|---|---|
| `lua/config/lazy.lua` | lazy.nvim bootstrap, LazyVim import | both |
| `lua/config/options.lua` | indent, colorcolumn, filetypes, WSL clipboard | both |
| `lua/config/keymaps.lua` | centred half-page scroll, Copilot accept | both |
| `lua/config/host.lua` | machine detection | both |
| `lazyvim.json` | LazyVim extras | both |
| `lua/plugins/ai.lua` | Copilot against InShared GHE | work |
| `lua/plugins/websites-monorepo.lua` | Nunjucks, `.worktrees` picker excludes | work |
| `lua/plugins/yspies-monorepo.lua` | LESS/emmet LSP, treesitter, picker excludes | personal |
| `lua/plugins/test.lua` | neotest → Jest and Playwright | personal |
| `lua/plugins/{colorscheme,diffview,oil}.lua` | Catppuccin Mocha, diffview, Oil | both |

## Indentation is 4 spaces on both machines

`options.lua` sets it; the websites monorepo's `.editorconfig` agrees and Neovim
applies that natively, and the yspies monorepo ships no `.editorconfig`. This
governs typing, not saved output — prettier reformats ts/html/json/less on save.

## What the personal machine wires up

Stack: Angular 21 + NestJS 11 on Nx 22 / pnpm, LESS for styling (232 files, no
SCSS), Python 3.12 under uv in `libs/shared/python-core`, Drizzle SQL
migrations, Playwright + Jest.

| Concern | Handled by |
|---|---|
| TS, Angular templates, eslint | `lang.typescript` + `lang.angular` extras → vtsls, angularls, eslint |
| LESS | `cssls` (unknown-at-rule lint off for PrimeUIX) + `emmet_ls`, prettier via conform |
| Python | `lang.python` extra → pyright, ruff |
| SQL, TOML, XML, Nx `*.template` files | treesitter grammars; `.template` maps to `eruby` because 28 of 47 carry EJS tags |
| Unit tests | `neotest-jest`, config and cwd resolved from the nearest `jest.config.*` |
| E2E tests | `neotest-playwright`, anchored to the nearest `playwright.config.*` |

Both neotest adapters ship filename-only matchers that would each claim every
`*.spec.ts` in the workspace. `test.lua` replaces both matchers so exactly one
adapter owns each file.

## Known gaps

- **No treesitter grammar for LESS exists upstream.** Neovim's bundled
  `syntax/less.vim` handles highlighting; cssls does the semantic work.
- **`apps/api` Jest specs need Postgres.** Their `globalSetup` seeds a real
  database, so running one from the buffer starts the same fixture the CLI does.
- **Playwright runs boot servers.** `createApiBackedE2EConfig` starts the app
  and the API, so a `<leader>tt` on an e2e spec is a minutes-long operation, not
  an edit-loop one.

## Bootstrapping a new machine

```sh
stow -d ~/dotfiles -t ~ nvim
nvim --headless "+Lazy! restore" +qa   # plugins at the pinned commits
```

LSP servers and treesitter parsers install themselves the first time you open a
file of that language — mason-lspconfig pulls whatever `opts.servers` asks for.
Opening one file per language beats any install command; `:checkhealth` and
`:Mason` show what is still missing.

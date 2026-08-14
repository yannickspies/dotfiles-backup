-- Test runners for the yspies monorepo: Jest for unit/integration (11 project
-- configs across apps/ and libs/shared/), Playwright for the 6 *-e2e suites.
--
-- Adapters are registered by name; LazyVim's test.core extra resolves the
-- module and calls its setup/adapter/__call entry point for us.
local host = require("config.host")

if not host.is_personal then
  return {}
end

local JEST_CONFIGS = { "jest.config.ts", "jest.config.cts", "jest.config.js", "jest.config.mjs" }
local PLAYWRIGHT_CONFIGS = { "playwright.config.ts", "playwright.config.js" }

---@param file string
---@param names string[]
---@return string|nil
local function find_up(file, names)
  return vim.fs.find(names, { upward = true, path = vim.fs.dirname(file) })[1]
end

--- Nearest jest config walking up from a spec file.
--- Nx keeps one per project (apps/api/jest.config.ts, libs/shared/util/jest.config.ts, ...)
--- with a root-level aggregator as the last resort, so "nearest wins" is right.
---@param file string
---@return string|nil
local function jest_config(file)
  return find_up(file, JEST_CONFIGS)
end

--- neotest-jest's own detector requires a `jest` entry in the nearest
--- package.json. Nx library package.jsons (libs/shared/util/package.json and
--- friends) declare only runtime deps, so every lib spec was being classified
--- as "not a test file". Match on the repo's actual convention instead.
---@param file string?
---@return boolean
local function is_jest_spec(file)
  if not file then
    return false
  end
  if not (file:match("%.spec%.[cm]?[jt]sx?$") or file:match("%.test%.[cm]?[jt]sx?$")) then
    return false
  end
  -- apps/api/jest.config.ts explicitly ignores these
  if file:match("%.e2e%-spec%.[cm]?ts$") then
    return false
  end
  -- Everything under apps/*-e2e is Playwright's; both adapters match *.spec.ts
  -- on filename alone, so keep the boundary explicit rather than relying on
  -- neotest's root resolution to break the tie.
  if find_up(file, PLAYWRIGHT_CONFIGS) then
    return false
  end
  return jest_config(file) ~= nil
end

--- The mirror image: neotest-playwright ships a filename-only matcher that
--- claims every *.spec.ts in the workspace, jest specs included. Anchor it to
--- a playwright.config.* ancestor so exactly one adapter owns each file.
---@param file string?
---@return boolean
local function is_playwright_spec(file)
  if not file or not file:match("%.spec%.[cm]?[jt]sx?$") then
    return false
  end
  return find_up(file, PLAYWRIGHT_CONFIGS) ~= nil
end

return {
  {
    "nvim-neotest/neotest",
    dependencies = {
      "nvim-neotest/neotest-jest",
      "thenbe/neotest-playwright",
    },
    opts = {
      adapters = {
        ["neotest-jest"] = {
          -- No jestCommand override: the adapter's default walks up to the
          -- nearest node_modules/.bin/jest, which pnpm hoists to the workspace
          -- root. Passing a wrapper (`pnpm exec jest --`) would put a bare `--`
          -- ahead of jest's own flags and turn them into positional args.
          isTestFile = is_jest_spec,
          jestConfigFile = jest_config,
          cwd = function(file)
            -- Project configs use relative rootDir/moduleNameMapper paths, so
            -- run from the directory that owns the config.
            local config = jest_config(file)
            return config and vim.fs.dirname(config) or vim.uv.cwd()
          end,
        },
        ["neotest-playwright"] = {
          options = {
            is_test_file = is_playwright_spec,
            persist_project_selection = true,
            enable_dynamic_test_discovery = true,
          },
        },
      },
    },
  },
}

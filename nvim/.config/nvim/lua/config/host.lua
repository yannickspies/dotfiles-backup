-- Which machine is this?
--
-- One config serves two boxes: the InShared work laptop and the personal WSL
-- box. Most of the config is shared; a few things (Copilot's GHE endpoint,
-- per-monorepo tweaks) only make sense on one of them.
--
-- Detection is by checkout path rather than hostname: hostnames change on
-- reimage and on WSL distro renames, the project checkouts do not.
local M = {}

local function has_dir(path)
  return vim.fn.isdirectory(vim.fn.expand(path)) == 1
end

--- InShared work laptop: the `websites` monorepo (Angular + Eleventy/Nunjucks).
M.is_work = has_dir("~/projects/frontend/websites")

--- Personal box: the yspies Nx monorepo (Angular + NestJS + Python).
M.is_personal = has_dir("~/projects/personal/yspies-monorepo")

return M

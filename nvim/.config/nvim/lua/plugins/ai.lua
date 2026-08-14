-- Copilot is work-only.
--
-- The token lives in InShared's GitHub Enterprise instance and there is no
-- Copilot subscription on the personal box, where Claude Code runs in its own
-- terminal pane instead. The extras stay listed in lazyvim.json so both
-- machines read the same in `:LazyExtras`; the specs below switch the plugins
-- off where they cannot authenticate. Without this, copilot.lua on the
-- personal box would sit there failing auth against a host it cannot reach.
local host = require("config.host")

return {
  -- InShared GHE instance; sign in with :Copilot auth.
  -- CopilotChat reuses the token copilot.lua writes to ~/.local/share/github-copilot;
  -- if chat fails against GHE, that integration is the first thing to check.
  {
    "zbirenbaum/copilot.lua",
    enabled = host.is_work,
    opts = {
      auth_provider_url = "https://inshared.ghe.com",
    },
  },
  { "fang2hou/blink-copilot", enabled = host.is_work },
  { "CopilotC-Nvim/CopilotChat.nvim", enabled = host.is_work },
}

return {
  -- InShared GitHub Enterprise instance; sign in with :Copilot auth.
  -- CopilotChat reuses the token copilot.lua writes to ~/.local/share/github-copilot;
  -- if chat fails against GHE, that integration is the first thing to check.
  {
    "zbirenbaum/copilot.lua",
    opts = {
      auth_provider_url = "https://inshared.ghe.com",
    },
  },
}

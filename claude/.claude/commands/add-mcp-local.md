---
argument-hint: <github-url>
description: Add MCP server from GitHub URL to local project .mcp.json
allowed-tools: Read, Write, Edit, WebFetch, Bash
---

Add the MCP server from GitHub repository `$1` to the local project's `.mcp.json` configuration.

## Steps:
1. Fetch the README from `$1` to extract the npx installation command
2. Parse the package name from the npx command (e.g., `@scope/package-name`)
3. Create or update `.mcp.json` in the current project directory
4. Add the MCP server configuration with:
   - Server name derived from the package name (last part after /)
   - Type: "stdio"
   - Command: "npx"
   - Args: ["-y", "package@latest"]
5. Preserve any existing MCP servers in the config
6. Format the JSON output properly

Example usage: `/add-mcp-local https://github.com/AgentDeskAI/browser-tools-mcp`

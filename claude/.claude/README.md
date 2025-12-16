# Claude Code Hooks Configuration

This directory contains a comprehensive set of hooks, commands, and agents for Claude Code, based on the [claude-code-hooks-mastery](https://github.com/disler/claude-code-hooks-mastery) repository.

## Directory Structure

```
.claude/
├── hooks/              # 8 lifecycle hooks using UV single-file scripts
├── commands/           # 10 custom slash commands
├── agents/             # 3 specialized sub-agents
├── output-styles/      # 8 response formatting styles
├── status_lines/       # 4 status line variants
├── ai_docs/            # Documentation and reference materials
├── settings.json       # Main hook configuration
├── settings.local.json # Machine-specific overrides (customize this!)
├── .gitignore         # Prevents committing secrets and runtime data
├── .env.sample        # Template for environment variables
└── .credentials.json.sample  # Template for API credentials
```

## Setup Instructions

### First Time Setup (New Machine)

1. **Stow the claude package:**
   ```bash
   cd ~/dotfiles
   stow claude
   ```
   This creates a symlink: `~/.claude` → `~/dotfiles/claude/.claude/`

2. **Create your secrets files:**
   ```bash
   cd ~/.claude
   cp .env.sample .env
   cp .credentials.json.sample .credentials.json
   ```

3. **Edit the secrets files with your actual API keys:**
   ```bash
   nvim ~/.claude/.env
   nvim ~/.claude/.credentials.json
   ```

4. **Customize settings.local.json for this machine:**
   ```bash
   nvim ~/.claude/settings.local.json
   ```
   Add any machine-specific permissions or additional directories.

5. **Test the setup:**
   ```bash
   cc  # Start Claude Code
   ```
   The `session_start` hook should fire automatically.

### Understanding the Hook Lifecycle

Claude Code fires hooks at different stages of interaction:

| Event | Hook | Can Block? | Purpose |
|-------|------|-----------|---------|
| Session starts | `session_start.py` | No | Load project context |
| User submits prompt | `user_prompt_submit.py` | Yes | Validate/enhance prompts |
| Before tool use | `pre_tool_use.py` | Yes | Security filtering |
| After tool use | `post_tool_use.py` | No | Log results |
| AI sends notification | `notification.py` | No | Custom alerts |
| AI stops responding | `stop.py` | Yes | Completion messages |
| Subagent completes | `subagent_stop.py` | Yes | Task summaries |
| Before compacting | `pre_compact.py` | No | Backup transcripts |

### Available Custom Commands

Run these commands in Claude Code:

- `/prime` - Load project context at session start
- `/commit` - Create concise git commits
- `/fix-build` - Build app and auto-fix errors
- `/question` - Answer questions without coding
- `/git_status` - Understand git repository state
- `/cleancode [path]` - Clean up messy code
- `/add-mcp-global <url>` - Add MCP server globally
- `/add-mcp-local <url>` - Add MCP server to project
- `/all_tools` - Show all available tools
- `/update_status_line` - Configure status line display

### Available Sub-Agents

Specialized agents for specific tasks:

- `hello-world-agent` - Simple greeting agent
- `work-completion-summary` - Proactive completion summaries with TTS
- `meta-agent` - Generates new agent configurations

### Available Output Styles

Response formatting options:

- `bullet-points.md` - Concise bullet format
- `genui.md` - UI/UX-focused responses
- `html-structured.md` - HTML-formatted output
- `markdown-focused.md` - Rich markdown with tables
- `table-based.md` - Data in tabular format
- `tts-summary.md` - Audio-friendly summaries
- `ultra-concise.md` - Minimal word responses
- `yaml-structured.md` - YAML configuration format

## Customization

### Adding New Commands

Create a new markdown file in `commands/`:

```bash
nvim ~/.claude/commands/my-command.md
```

Add command documentation with this format:

```markdown
# Command Name

Description of what this command does.

## Usage
/my-command [arguments]

## Examples
...
```

### Adding New Agents

Create a new agent definition in `agents/`:

```bash
nvim ~/.claude/agents/my-agent.md
```

Follow the structure of existing agents.

### Modifying Hooks

Edit hook scripts in `hooks/`. Each uses UV single-file scripts with embedded dependencies:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "anthropic>=0.39.0",
# ]
# ///

# Your hook logic here
```

### Machine-Specific Permissions

Edit `settings.local.json` to customize permissions for this machine:

```json
{
  "permissions": {
    "allow": [
      "Bash(git:*)",
      "Read(//your/custom/path/**)"
    ],
    "deny": ["Bash(rm -rf:*)"],
    "additionalDirectories": [
      "/path/to/additional/workspace"
    ]
  }
}
```

## Maintenance

### Updating from Upstream

Since this is version-controlled, you can track upstream changes:

```bash
cd ~/dotfiles
git pull  # Get updates if you've pushed to a remote
```

### Backup Important Data

Runtime data (logs, todos, debug info) is NOT version-controlled and stays in:
- `~/.claude/debug/`
- `~/.claude/todos/`
- `~/.claude/projects/`
- `~/.claude/shell-snapshots/`

Hook execution logs are tracked separately in: `~/dotfiles/logs/`

### Restowing After Changes

If you modify the dotfiles structure:

```bash
cd ~/dotfiles
stow -R claude  # Restow to update symlinks
```

## Troubleshooting

### Hooks Not Firing

1. Check hook permissions: `ls -la ~/.claude/hooks/`
2. All hooks should be executable: `chmod +x ~/.claude/hooks/*.py`
3. Verify UV is installed: `uv --version`
4. Check logs: `tail ~/.claude/logs/*.json`

### API Key Issues

1. Verify `.env` exists: `ls ~/.claude/.env`
2. Check API key format in `.env` and `.credentials.json`
3. Test keys with: `uv run ~/.claude/hooks/utils/llm/oai.py`

### Symlink Problems

1. Verify symlink: `ls -la ~/.claude`
2. Should show: `.claude -> ../dotfiles/claude/.claude`
3. If broken, remove and restow: `rm ~/.claude && cd ~/dotfiles && stow claude`

## Security Notes

- **Never commit `.env` or `.credentials.json`** - these contain API keys!
- The `.gitignore` file protects against accidental commits
- The `pre_tool_use.py` hook blocks dangerous commands like `rm -rf`
- Review any new hooks before running them

## Resources

- [Claude Code Hooks Documentation](./ai_docs/cc_hooks_docs.md)
- [UV Single-File Scripts](./ai_docs/uv-single-file-scripts.md)
- [Custom Slash Commands](./ai_docs/anthropic_custom_slash_commands.md)
- [Sub-Agents Guide](./ai_docs/anthropic_docs_subagents.md)
- [Original Repository](https://github.com/disler/claude-code-hooks-mastery)

## Contributing

Improvements to hooks, commands, or agents are welcome! Since this is version-controlled in your dotfiles:

1. Make changes to files in `~/dotfiles/claude/.claude/`
2. Test thoroughly
3. Commit with descriptive messages
4. Push to your dotfiles repository

---

*Managed via GNU Stow - Part of your dotfiles configuration*

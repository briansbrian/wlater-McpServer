# wlater MCP Server

Connect your AI assistant to Google Keep. Search, read, and manage your notes and lists through natural conversation.

## Installation

```bash
pip install wlater-mcp
```

## Setup

Run the setup wizard to configure your credentials:

```bash
wlater-setup
```

Choose your authentication method:
- **Automated**: Opens Chrome and logs you in automatically
- **Manual**: Enter your credentials directly

## Configuration

Add to your MCP client's config file (e.g., `mcp.json`):

```json
{
  "mcpServers": {
    "wlater": {
      "command": "python",
      "args": ["-m", "wlater_mcp.server"]
    }
  }
}
```

Restart your AI assistant and you're ready!

## Usage

Talk to your AI naturally:

- "Show me all my pinned notes"
- "What's on my shopping list?"
- "Find notes with images attached"
- "Check off 'buy milk' from my grocery list"
- "Create a note called 'Meeting Notes'"
- "Add 'call dentist' to my todo list"
- "Find notes labeled 'work'"
- "Make my important note red and pin it"
- "Sort my shopping list alphabetically"

All changes are previewed before being saved to Google Keep.

## Features

**What You Can Do:**
- ✅ Search and read all your notes
- ✅ Filter by labels, colors, pins, and archived status
- ✅ View attached images, drawings, and audio
- ✅ Create new notes and todo lists
- ✅ Check off items on your shopping lists
- ✅ Update note content, titles, and colors
- ✅ Pin important notes and archive old ones
- ✅ Organize with labels
- ✅ Sort your lists alphabetically
- ✅ Share notes with collaborators

**How It Keeps You Safe:**
- 🔒 Your login credentials are stored securely in your system keyring
- 👀 Preview every change before it's saved
- 🚫 Can't delete notes ,Only Trash\Untrash (use Google Keep app for that)
- ⏸️ All changes wait for your approval—nothing happens automatically

## Troubleshooting

**"Master token not found"**
```bash
wlater-setup
```

**"Authentication failed"**  
Your token may have expired. Re-run setup.

**Server not appearing**  
Check your config file paths and restart your MCP client.

## Security

- Credentials stored in your system keyring (Windows Credential Locker, macOS Keychain, Linux Secret Service)
- Preview all changes before syncing
- No automatic modifications
- Delete operations not exposed

## Links

- [GitHub Repository](https://github.com/briansbrian/wlater-McpServer)
- [Report Issues](https://github.com/briansbrian/wlater-McpServer/issues)
- [Model Context Protocol](https://modelcontextprotocol.io)

## License

MIT License - See [LICENSE](LICENSE) for details

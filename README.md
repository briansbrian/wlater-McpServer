# wlater MCP Server

A Model Context Protocol (MCP) server that provides AI assistants with secure, read-only access to Google Keep notes and lists.

FOR INSTALLATION PLEASE VISIT build branch
https://github.com/briansbrian/wlater-McpServer/tree/build

![Image_fx(19)](https://github.com/user-attachments/assets/eb5d595d-8433-470c-8565-1fad6a3a232e)


## Features

### Tier 1: Read-Only Access
- **Query & Search**: List, search, and retrieve Keep data
- **List Management**: View todo items with checked/unchecked status
- **Label Support**: Filter and organize notes by labels
- **Media Access**: Retrieve metadata and download links for images, drawings, and audio

### Tier 2: Safe Modifications
- **Note Creation**: Create text notes and todo lists
- **List Operations**: Check/uncheck items, add new items to lists
- **Note Updates**: Modify titles, text content, colors, pin/archive status
- **Label Management**: Create labels, add/remove labels from notes
- **Preview-Before-Sync**: Review all changes before saving to Google Keep
- **Explicit Sync Control**: Manual sync ensures no accidental modifications

### Security
- **Secure Credential Storage**: Master tokens stored in OS-native keyring (Windows Credential Locker, macOS Keychain, Linux Secret Service)
- **No Auto-Sync**: All Tier 2 changes require explicit user confirmation via `sync_changes()`
- **Destructive Operations Blocked**: Delete and trash operations are never exposed

## Security Model

The server implements a tiered exposure model:
- **Tier 1 (Implemented)**: Read-only operations - list, search, get note details
- **Tier 2 (Implemented)**: Modifications with explicit sync - create, update, archive notes and lists
- **Tier 3 (Not Exposed)**: Destructive operations - delete, trash

### Tier 2 Safety Features

Tier 2 operations follow a **preview-before-sync** workflow:

1. **Local Changes Only**: All modifications update local state without touching Google Keep servers
2. **Preview Every Change**: Each operation returns a preview showing what changed
3. **Explicit Sync Required**: Changes only reach Google Keep when you explicitly call `sync_changes()`
4. **Batch Operations**: Make multiple changes, review them all, then sync once
5. **No Auto-Sync**: The server NEVER automatically syncs - you have complete control

This ensures you can review all changes before they're saved, preventing accidental modifications.

## Installation

### Prerequisites

- Python 3.8 or higher
- Chrome browser (for automated authentication)
- ChromeDriver (for automated authentication, optional if using manual mode)

### Setup Steps

1. **Clone the repository** (if not already done):
   ```bash
   git clone https://github.com/yourusername/wlater-mcp.git
   cd wlater-mcp
   ```

2. **Create and activate virtual environment**:
   
   **Windows:**
   ```cmd
   python -m venv .venv
   .venv\Scripts\activate
   ```
   
   **Linux/macOS:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
   
   **Note**: Always activate the virtual environment before running any Python commands. You'll know it's activated when you see `(.venv)` at the beginning of your command prompt.

3. **Install dependencies** (with virtual environment activated):
   ```bash
   pip install -r requirements.txt
   ```

4. **Run setup to store credentials** (with virtual environment activated):
   ```bash
   python src/setup.py
   ```
   
   You'll be prompted to choose:
   - **(s) Automated selenium authentication**: Opens browser, automates login, extracts token automatically
   - **(m) Manual credential entry**: Enter email, master token, and android_id manually
   
   The setup will:
   - Store your master token securely in OS keyring
   - Create a `.wlater` config file in your home directory
   - Display next steps for MCP configuration
   
   **Important**: Keep your virtual environment activated during setup!

## MCP Configuration for Kiro

### Locate Your MCP Configuration File

Kiro's MCP configuration is stored in:
- **Workspace level**: `.kiro/settings/mcp.json` (in your project folder)
- **User level**: `~/.kiro/settings/mcp.json` (global configuration)

You can also open it via Kiro's command palette: Search for "MCP" and select "Open MCP Configuration"

### Add wlater Server Configuration

Add the following to your `mcp.json` file. **Replace the paths with your actual project location**:

**Windows Example:**
```json
{
  "mcpServers": {
    "wlater": {
      "command": "C:/Users/YourUsername/projects/wlater-mcp/.venv/Scripts/python.exe",
      "args": ["C:/Users/YourUsername/projects/wlater-mcp/src/server.py"],
      "disabled": false
    }
  }
}
```

**Linux/macOS Example:**
```json
{
  "mcpServers": {
    "wlater": {
      "command": "/home/yourusername/projects/wlater-mcp/.venv/bin/python",
      "args": ["/home/yourusername/projects/wlater-mcp/src/server.py"],
      "disabled": false
    }
  }
}
```

### Critical Configuration Notes

1. **Use Full Absolute Paths**: Always use complete paths, not relative paths like `./` or `~/`
2. **Virtual Environment Python**: Point to `.venv/Scripts/python.exe` (Windows) or `.venv/bin/python` (Linux/macOS), NOT system Python
3. **Forward Slashes**: Use forward slashes (`/`) even on Windows for JSON compatibility
4. **No Trailing Slashes**: Don't add trailing slashes to directory paths

### Verify Your Configuration

To find your exact paths:

**Windows:**
```cmd
cd C:\path\to\wlater-mcp
cd
echo %CD%\.venv\Scripts\python.exe
```

**Linux/macOS:**
```bash
cd /path/to/wlater-mcp
pwd
echo "$(pwd)/.venv/bin/python"
```

### Activate the Server

After adding the configuration:
1. **Restart Kiro**, or
2. **Reconnect MCP servers** from the MCP Server view in Kiro's sidebar, or
3. Use command palette: "MCP: Reconnect Servers"

The wlater server should now appear in your MCP tools list.

## Available MCP Tools

The server provides two tiers of tools:
- **Tier 1 Tools**: Read-only operations (safe, no sync required)
- **Tier 2 Tools**: Modification operations (require explicit sync to save changes)

### Understanding the Preview-Before-Sync Workflow

All Tier 2 tools follow this safety pattern:

```
1. Call modification tool → Changes made locally (NOT synced)
2. Review preview response → See what changed
3. Call sync_changes() → Push changes to Google Keep
```

**Important**: Changes are NOT saved to Google Keep until you explicitly call `sync_changes()`. This gives you complete control and prevents accidental modifications.

---

## Tier 1 Tools (Read-Only)

### `check_credentials`
**Purpose**: Check if credentials are configured and valid.

**Parameters**: None

**Returns**: 
```json
{
  "configured": true,
  "email": "user@gmail.com",
  "message": "Credentials found and valid"
}
```

**Use Case**: Verify setup before using other tools

---

### `list_all_notes`
**Purpose**: List all notes and lists from Google Keep.

**Parameters**: None

**Returns**: Array of notes with basic metadata
```json
[
  {
    "note_id": "abc123",
    "title": "My Note",
    "note_type": "Note",
    "pinned": false,
    "archived": false,
    "color": "DEFAULT"
  }
]
```

**Limits**: Returns up to 1000 notes (excludes trashed notes)

---

### `get_note`
**Purpose**: Get detailed content for a specific note by ID.

**Parameters**:
- `note_id` (string, required): Google Keep note ID

**Returns**: Full note details
```json
{
  "note_id": "abc123",
  "title": "My Note",
  "text": "Note content here",
  "note_type": "Note",
  "color": "BLUE",
  "pinned": false,
  "archived": false,
  "labels": [{"id": "label1", "name": "Work"}],
  "timestamps": {
    "created": "2024-01-01T00:00:00Z",
    "updated": "2024-01-15T10:00:00Z",
    "edited": "2024-01-15T10:00:00Z"
  }
}
```

**Errors**: Raises exception if note_id doesn't exist

---

### `get_list_items`
**Purpose**: Get list items with checked status for todo lists.

**Parameters**:
- `list_id` (string, required): Google Keep list ID

**Returns**: List items organized by status
```json
{
  "list_id": "xyz789",
  "title": "Shopping List",
  "all_items": [
    {"item_id": "i1", "text": "Milk", "checked": false, "sort": 1},
    {"item_id": "i2", "text": "Bread", "checked": true, "sort": 2}
  ],
  "checked_items": [...],
  "unchecked_items": [...]
}
```

**Errors**: Returns error if note is not a List type

---

### `search_notes`
**Purpose**: Search notes with optional filters.

**Parameters**:
- `query` (string, optional): Text to search for in note content
- `pinned` (boolean, optional): Filter by pinned status
- `archived` (boolean, optional): Filter by archived status
- `trashed` (boolean, optional): Filter by trashed status
- `colors` (array of strings, optional): Filter by colors (e.g., `["RED", "BLUE"]`)
- `labels` (array of strings, optional): Filter by label names

**Returns**: Array of matching notes (same format as `list_all_notes`)

**Limits**: Returns up to 100 results

**Examples**:
- Search for "project": `search_notes(query="project")`
- Find pinned notes: `search_notes(pinned=true)`
- Find work notes: `search_notes(labels=["Work"])`
- Multiple filters: `search_notes(query="meeting", pinned=true, colors=["BLUE"])`

---

### `list_labels`
**Purpose**: List all labels sorted alphabetically.

**Parameters**: None

**Returns**: Array of labels
```json
[
  {"label_id": "label1", "name": "Personal"},
  {"label_id": "label2", "name": "Work"}
]
```

---

### `find_label`
**Purpose**: Find a label by name (case-insensitive).

**Parameters**:
- `name` (string, required): Label name to search for

**Returns**: Label object or null
```json
{
  "label_id": "label1",
  "name": "Work"
}
```

**Note**: Returns first match if multiple labels have similar names

---

## Tier 2 Tools (Modifications - Require Sync)

All Tier 2 tools modify local state only. You MUST call `sync_changes()` to save changes to Google Keep.

### List Item Operations

#### `update_list_item_checked`
**Purpose**: Check or uncheck a todo item in a list.

**Parameters**:
- `list_id` (string, required): Google Keep list ID
- `item_id` (string, required): List item ID
- `checked` (boolean, required): New checked status (true to check, false to uncheck)

**Returns**: Preview of change
```json
{
  "success": true,
  "operation": "update_list_item_checked",
  "preview": {
    "list_id": "abc123",
    "list_title": "Shopping List",
    "item_id": "item456",
    "item_text": "Buy milk",
    "old_value": false,
    "new_value": true
  },
  "synced": false,
  "message": "Item checked status updated locally. Call sync_changes() to save to Google Keep."
}
```

**Example Workflow**:
```
1. User: "Check off 'Buy milk' from my shopping list"
2. AI calls: update_list_item_checked(list_id="abc123", item_id="item456", checked=true)
3. AI shows preview: "I've checked 'Buy milk'. Call sync_changes() to save?"
4. User: "Yes, save it"
5. AI calls: sync_changes()
6. AI confirms: "Changes synced to Google Keep"
```

---

#### `add_list_item`
**Purpose**: Add a new item to an existing list.

**Parameters**:
- `list_id` (string, required): Google Keep list ID
- `text` (string, required): Item text
- `checked` (boolean, optional): Initial checked status (default: false)
- `sort` (integer, optional): Sort order

**Returns**: Preview with new item details
```json
{
  "success": true,
  "operation": "add_list_item",
  "preview": {
    "list_id": "abc123",
    "list_title": "Shopping List",
    "item_text": "Buy eggs",
    "checked": false
  },
  "synced": false,
  "message": "Item added locally. Call sync_changes() to save to Google Keep."
}
```

---

### Note Creation

#### `create_note`
**Purpose**: Create a new text note.

**Parameters**:
- `title` (string, optional): Note title (default: "")
- `text` (string, optional): Note text content (default: "")

**Returns**: Preview with note details
```json
{
  "success": true,
  "operation": "create_note",
  "preview": {
    "note_id": "new123",
    "title": "Meeting Notes",
    "text": "Discussed project timeline..."
  },
  "synced": false,
  "message": "Note created locally. Call sync_changes() to save to Google Keep."
}
```

---

#### `create_list`
**Purpose**: Create a new todo list with items.

**Parameters**:
- `title` (string, optional): List title (default: "")
- `items` (array of objects, optional): List items with format `[{"text": "item text", "checked": false}, ...]`

**Returns**: Preview with list details
```json
{
  "success": true,
  "operation": "create_list",
  "preview": {
    "list_id": "new456",
    "title": "Weekend Tasks",
    "items": [
      {"text": "Clean garage", "checked": false},
      {"text": "Grocery shopping", "checked": false}
    ]
  },
  "synced": false,
  "message": "List created locally. Call sync_changes() to save to Google Keep."
}
```

**Example**:
```python
create_list(
  title="Weekend Tasks",
  items=[
    {"text": "Clean garage", "checked": False},
    {"text": "Grocery shopping", "checked": False}
  ]
)
```

---

### Note Updates

#### `update_note_title`
**Purpose**: Update a note's title.

**Parameters**:
- `note_id` (string, required): Google Keep note ID
- `title` (string, required): New title

**Returns**: Preview showing old and new title
```json
{
  "success": true,
  "operation": "update_note_title",
  "preview": {
    "note_id": "abc123",
    "old_title": "Meeting",
    "new_title": "Meeting Notes - Q4 Planning"
  },
  "synced": false,
  "message": "Note title updated locally. Call sync_changes() to save."
}
```

---

#### `update_note_text`
**Purpose**: Update a note's text content.

**Parameters**:
- `note_id` (string, required): Google Keep note ID
- `text` (string, required): New text content

**Returns**: Preview showing old and new text

**Note**: Only works on Note type, not List type. Lists don't have text content - use `add_list_item()` instead.

**Error Example**:
```json
{
  "success": false,
  "error": "TypeError",
  "message": "Note abc123 is a List type. Lists do not support text updates. Use add_list_item() instead."
}
```

---

### Note Properties

#### `update_note_color`
**Purpose**: Change a note's color.

**Parameters**:
- `note_id` (string, required): Google Keep note ID
- `color` (string, required): Color name

**Valid Colors**: White, Red, Orange, Yellow, Green, Teal, Blue, DarkBlue, Purple, Pink, Brown, Gray

**Returns**: Preview with new color
```json
{
  "success": true,
  "operation": "update_note_color",
  "preview": {
    "note_id": "abc123",
    "note_title": "Important Tasks",
    "old_color": "DEFAULT",
    "new_color": "RED"
  },
  "synced": false,
  "message": "Note color updated locally. Call sync_changes() to save."
}
```

---

#### `update_note_pinned`
**Purpose**: Pin or unpin a note.

**Parameters**:
- `note_id` (string, required): Google Keep note ID
- `pinned` (boolean, required): New pinned status (true to pin, false to unpin)

**Returns**: Preview with new pinned status

---

#### `update_note_archived`
**Purpose**: Archive or unarchive a note.

**Parameters**:
- `note_id` (string, required): Google Keep note ID
- `archived` (boolean, required): New archived status (true to archive, false to unarchive)

**Returns**: Preview with new archived status

---

### Label Operations

#### `create_label`
**Purpose**: Create a new label.

**Parameters**:
- `name` (string, required): Label name

**Returns**: Preview with label details
```json
{
  "success": true,
  "operation": "create_label",
  "preview": {
    "label_id": "label789",
    "name": "Project Alpha"
  },
  "synced": false,
  "message": "Label created locally. Call sync_changes() to save to Google Keep."
}
```

---

#### `add_label_to_note`
**Purpose**: Add a label to a note.

**Parameters**:
- `note_id` (string, required): Google Keep note ID
- `label_name` (string, required): Label name to add

**Returns**: Preview with updated labels
```json
{
  "success": true,
  "operation": "add_label_to_note",
  "preview": {
    "note_id": "abc123",
    "note_title": "Meeting Notes",
    "labels": ["Work", "Project Alpha"]
  },
  "synced": false,
  "message": "Label added locally. Call sync_changes() to save."
}
```

**Error**: Returns error if label doesn't exist. Create the label first with `create_label()`.

---

#### `remove_label_from_note`
**Purpose**: Remove a label from a note.

**Parameters**:
- `note_id` (string, required): Google Keep note ID
- `label_name` (string, required): Label name to remove

**Returns**: Preview with updated labels

---

### Sync Control (Critical)

#### `sync_changes`
**Purpose**: Sync all pending changes to Google Keep servers.

**Parameters**: None

**Returns**: Confirmation with sync details
```json
{
  "success": true,
  "operation": "sync",
  "changes_synced": 3,
  "timestamp": "2025-11-14T12:34:56.789Z",
  "message": "Successfully synced 3 changes to Google Keep"
}
```

**This is the ONLY way changes are saved to Google Keep.** All modification tools update local state only - you must explicitly call `sync_changes()` to persist changes.

**Best Practice**: Review pending changes with `get_pending_changes()` before syncing.

---

#### `get_pending_changes`
**Purpose**: Preview all pending changes before syncing.

**Parameters**: None

**Returns**: Structured preview of all changes
```json
{
  "has_changes": true,
  "change_count": 3,
  "changes": [
    {
      "note_id": "abc123",
      "note_title": "Shopping List",
      "change_type": "list_item_checked",
      "details": "Checked: Buy milk"
    },
    {
      "note_id": "def456",
      "note_title": "Ideas",
      "change_type": "note_created",
      "details": "New note created"
    },
    {
      "note_id": "ghi789",
      "note_title": "Meeting Notes",
      "change_type": "note_title_updated",
      "details": "Old: 'Meeting' → New: 'Meeting Notes'"
    }
  ]
}
```

**Use Case**: Call this before `sync_changes()` to review what will be saved.

---

#### `refresh_notes`
**Purpose**: Refresh local cache from Google Keep server.

**Parameters**: None

**Returns**: Confirmation message
```json
{
  "success": true,
  "operation": "refresh",
  "message": "Cache refreshed from Google Keep at 2025-11-14T12:34:56.789Z"
}
```

**Important**: If you have pending local changes, they will be synced during the refresh operation. Use `get_pending_changes()` first if you want to review them.

**Use Case**: Fetch notes created outside the MCP server (e.g., in the Google Keep mobile app).

---

### Media Operations (Read-Only)

#### `get_note_media`
**Purpose**: Get all media attachments from a note.

**Parameters**:
- `note_id` (string, required): Google Keep note ID

**Returns**: Media metadata
```json
{
  "success": true,
  "note_id": "abc123",
  "note_title": "Vacation Photos",
  "media": {
    "images": [
      {
        "blob_id": "img_001",
        "type": "image",
        "width": 1920,
        "height": 1080,
        "byte_size": 245678,
        "extracted_text": "Beach sunset"
      }
    ],
    "drawings": [
      {
        "blob_id": "draw_001",
        "type": "drawing",
        "extracted_text": "Diagram of process"
      }
    ],
    "audio": [
      {
        "blob_id": "audio_001",
        "type": "audio",
        "length": 120.5
      }
    ]
  },
  "total_media": 3
}
```

**Note**: Returns empty lists if note has no media attachments.

---

#### `get_media_link`
**Purpose**: Get download URL for a media blob.

**Parameters**:
- `note_id` (string, required): Google Keep note ID
- `blob_id` (string, required): Media blob ID (from `get_note_media()`)

**Returns**: Download URL
```json
{
  "success": true,
  "note_id": "abc123",
  "blob_id": "img_001",
  "media_type": "image",
  "download_url": "https://keep.google.com/media/v2/...",
  "expires": "URL is temporary and may expire"
}
```

**Use Case**: Get the blob_id from `get_note_media()`, then call this to get the download URL.

**Warning**: URLs are temporary and may expire. Download media promptly if needed.

---

## Usage Examples

### Tier 1 (Read-Only) Examples

Once configured in Kiro, you can query your Keep data through natural language:

- "Show me all my pinned notes"
- "Find notes about project planning"
- "What's on my shopping list?"
- "Show me unchecked items in my todo list"
- "Find all notes with the 'work' label"
- "Show me images attached to my vacation note"

### Tier 2 (Modification) Examples

You can also modify your Keep data with explicit sync control:

**Managing Todo Lists:**
- "Check off 'Buy milk' from my shopping list" → Preview → "Save these changes" → Synced
- "Add 'Buy eggs' to my shopping list" → Preview → Sync when ready

**Creating Notes:**
- "Create a note titled 'Meeting Notes' with the text 'Discussed Q4 goals'" → Preview → Sync
- "Create a todo list called 'Weekend Tasks' with items: Clean garage, Grocery shopping" → Preview → Sync

**Updating Notes:**
- "Change the title of my meeting note to 'Q4 Planning Meeting'" → Preview → Sync
- "Make my important tasks note red" → Preview → Sync
- "Pin my project ideas note" → Preview → Sync

**Label Management:**
- "Create a label called 'Project Alpha'" → Preview → Sync
- "Add the 'Work' label to my meeting notes" → Preview → Sync

**Batch Operations:**
- "Check off three items from my todo list" → Preview all changes → "Show me pending changes" → Review → Sync all at once

**Safety Workflow:**
```
User: "Check off 'Buy milk' and add 'Buy eggs' to my shopping list"
AI: Makes both changes locally, shows preview
AI: "I've updated your shopping list:
     - Checked: Buy milk
     - Added: Buy eggs
     
     These changes are local only. Would you like me to sync them to Google Keep?"
User: "Yes, save them"
AI: Calls sync_changes()
AI: "Successfully synced 2 changes to Google Keep"
```

## Troubleshooting

### Setup and Installation Issues

#### Virtual Environment Not Activating

**Problem**: Command prompt doesn't show `(.venv)` prefix

**Windows Solution**:
```cmd
# Try activating with full path
C:\path\to\wlater-mcp\.venv\Scripts\activate.bat

# If PowerShell execution policy blocks it:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Linux/macOS Solution**:
```bash
# Ensure you're using source, not just running the script
source .venv/bin/activate

# Check if venv was created properly
ls -la .venv/bin/
```

#### Module Not Found Errors

**Problem**: `ModuleNotFoundError: No module named 'fastmcp'` or similar

**Solution**:
1. Ensure virtual environment is activated (you should see `(.venv)` in prompt)
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Verify installation: `pip list | grep fastmcp`

---

### Authentication and Credential Issues

#### "Master token not found in keyring"

**Problem**: Server can't find stored credentials

**Solution**:
1. Verify `.wlater` file exists in your home directory:
   - Windows: `C:\Users\YourUsername\.wlater`
   - Linux/macOS: `~/.wlater`
2. Check keyring access:
   ```bash
   python -c "import keyring; print(keyring.get_keyring())"
   ```
3. Re-run setup with venv activated:
   ```bash
   python src/setup.py
   ```

#### "Authentication failed. Token may be expired"

**Problem**: Master token is no longer valid

**Solution**:
1. Delete existing credentials:
   - Remove `~/.wlater` file
   - Clear keyring entry (or let setup overwrite it)
2. Re-run setup: `python src/setup.py`
3. Choose selenium mode for fresh token

#### Platform/Username Changes

**Symptom**: Server detects platform or username mismatch

**Automatic Fix**: The server will automatically:
- Detect platform/username changes
- Regenerate android_id using deterministic base-36 encoding
- Update `.wlater` file with new values

**How Android ID Generation Works**:
- Uses reversible base-36 encoding algorithm
- Structure: `776c61` (wlater) + platform code + encoded username
- Platform codes: 01=Windows, 02=Linux, 03=macOS, etc.
- Username normalized to 6 chars (lowercase, alphanumeric, padded)
- Total: 16 hexadecimal characters
- Deterministic: same username + platform = same ID
- Reversible: can decode username for breach investigation

**Manual Fix** (if needed):
1. Delete `~/.wlater` file
2. Re-run `python src/setup.py`

---

### Selenium Authentication Issues

#### "ChromeDriver not found"

**Problem**: Selenium can't find ChromeDriver executable

**Solution**:
- **Option 1**: Install via package manager
  - Windows: `choco install chromedriver`
  - macOS: `brew install chromedriver`
  - Linux: `sudo apt install chromium-chromedriver`
- **Option 2**: Download manually from https://chromedriver.chromium.org/
  - Add to PATH or place in project directory
- **Option 3**: Use manual credential entry mode instead

#### "CAPTCHA appears during login"

**Problem**: Google shows CAPTCHA during automated login

**Solution**:
1. Solve the CAPTCHA in the browser window that opens
2. The script will wait for you to complete it
3. Continue with the authentication flow
4. If CAPTCHA persists, try manual credential entry mode

#### Browser Closes Immediately

**Problem**: Browser window opens and closes without logging in

**Solution**:
1. Check Chrome and ChromeDriver versions match
2. Update ChromeDriver to match your Chrome version
3. Try running with visible browser (check selenium script settings)

---

### MCP Server Issues

#### Server Not Appearing in Kiro

**Problem**: wlater server doesn't show up in MCP tools list

**Solution**:
1. **Verify MCP configuration**:
   - Open `.kiro/settings/mcp.json` or `~/.kiro/settings/mcp.json`
   - Check paths are absolute and correct
   - Ensure forward slashes used (even on Windows)
   
2. **Test paths manually**:
   ```cmd
   # Windows - verify Python path exists
   dir "C:\path\to\wlater-mcp\.venv\Scripts\python.exe"
   
   # Linux/macOS
   ls -la /path/to/wlater-mcp/.venv/bin/python
   ```

3. **Reconnect MCP servers**:
   - Use Kiro command palette: "MCP: Reconnect Servers"
   - Or restart Kiro completely

4. **Check Kiro logs** for error messages

#### "Server failed to start" Error

**Problem**: MCP server fails during startup

**Solution**:
1. **Test server manually** (with venv activated):
   ```bash
   python src/server.py
   ```
   This will show detailed error messages

2. **Common causes**:
   - Credentials not configured: Run `python src/setup.py`
   - Wrong Python path: Use venv Python, not system Python
   - Missing dependencies: Run `pip install -r requirements.txt`

3. **Verify credentials**:
   ```bash
   python -c "from src.credentials import load_credentials; print(load_credentials())"
   ```

#### Tools Return Errors

**Problem**: MCP tools fail when invoked

**Solution**:
1. **Check credentials first**:
   - Use `check_credentials` tool
   - Verify it returns `"configured": true`

2. **Re-authenticate if needed**:
   ```bash
   python src/setup.py
   ```

3. **Check network connectivity** to Google Keep

4. **Review error messages** - they usually indicate the specific issue

---

### Configuration Path Issues

#### "Cannot find mcp.json"

**Problem**: Don't know where to add MCP configuration

**Solution**:
1. **Create workspace config**:
   - Create `.kiro/settings/` folder in your project
   - Create `mcp.json` file there
   
2. **Or use user config**:
   - Windows: `C:\Users\YourUsername\.kiro\settings\mcp.json`
   - Linux/macOS: `~/.kiro/settings/mcp.json`

3. **Or use Kiro command palette**:
   - Search "MCP" → "Open MCP Configuration"

#### Wrong Python Executable

**Problem**: Using system Python instead of venv Python

**Symptom**: "Module not found" errors even though dependencies are installed

**Solution**:
Update `mcp.json` to use venv Python:
```json
{
  "mcpServers": {
    "wlater": {
      "command": "C:/full/path/to/wlater-mcp/.venv/Scripts/python.exe",
      "args": ["C:/full/path/to/wlater-mcp/src/server.py"]
    }
  }
}
```

---

### Getting Help

If you're still experiencing issues:

1. **Check credentials**: Run `python src/setup.py` again
2. **Test manually**: Run `python src/server.py` with venv activated
3. **Review logs**: Check Kiro's MCP server logs for detailed errors
4. **Verify paths**: Ensure all paths in `mcp.json` are absolute and correct
5. **Open an issue**: Include error messages and your configuration (remove sensitive data)

## Development

### Project Structure

```
wlater-mcp/
├── .venv/                    # Virtual environment
├── src/                      # Source code
│   ├── server.py            # Main MCP server entry point
│   ├── keep_client.py       # Google Keep API wrapper
│   ├── credentials.py       # Credential management
│   └── setup.py             # One-time credential setup
├── Scripts/                  # Utility scripts
│   └── selenium_get_oauth.py # Automated credential retrieval
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

### Running Tests

```bash
# Activate virtual environment first
pytest

# With coverage
pytest --cov=src --cov-report=html

# Type checking
mypy src/
```

### Code Formatting

```bash
black src/
```

## Security Considerations

- **Master tokens** are stored in OS-native keyring only (never in files)
- **Config file** (`.wlater`) contains no sensitive data
- **Tier 1 tools** are read-only with no side effects
- **Tier 2 tools** require explicit sync - no automatic modifications
- **Preview-before-sync** workflow prevents accidental changes
- **No destructive operations** - delete and trash are never exposed (Tier 3)
- **Token validation** before storage (must start with `aas_et/`)
- **No token logging** or error message exposure
- **Android ID generation**:
  - Uses deterministic base-36 encoding (same user = same ID)
  - Reversible for breach investigation (can decode username)
  - Structure: `776c61` (wlater) + platform code + encoded username
  - Privacy-conscious: usernames normalized, not directly readable
  - See `Docs/android_id_proposal.md` for full specification

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues, questions, or feature requests, please open an issue on GitHub.



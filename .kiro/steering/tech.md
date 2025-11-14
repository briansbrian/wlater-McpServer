# Technology Stack

## Core Technologies

- **Language**: Python 3.x
- **MCP Framework**: FastMCP - Simplifies MCP server development with decorators and automatic tool registration
- **Google Keep API**: gkeepapi - Unofficial Python client for Google Keep
- **Credential Storage**: keyring - OS-native credential management

## Key Libraries

```
fastmcp>=0.1.0          # MCP server framework
gkeepapi>=1.0.0         # Google Keep API client
keyring>=24.0.0         # OS keyring access
selenium>=4.0.0         # Automated OAuth token retrieval
gpsoauth                # Google OAuth token exchange
```

## Project Structure

```
wlater-mcp/
├── .venv/                    # Virtual environment (isolated dependencies)
├── src/                      # Source code (all Python modules)
│   ├── server.py            # Main MCP server entry point
│   ├── keep_client.py       # Google Keep API wrapper
│   ├── credentials.py       # Credential management
│   ├── tools.py             # MCP tool definitions
│   └── setup.py             # One-time credential setup
├── Scripts/                  # Utility scripts
│   └── selenium_get_oauth.py # Automated credential retrieval
├── backup/                   # Legacy/backup scripts
├── Docs/                     # Documentation and design notes
├── .kiro/                    # Kiro IDE configuration
│   ├── specs/               # Feature specifications
│   └── steering/            # AI assistant guidance (this file)
└── requirements.txt         # Python dependencies
```

## Common Commands

### Environment Setup

```bash
# Windows - Activate virtual environment
.venv\Scripts\activate

# Linux/macOS - Activate virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Credential Setup

```bash
# Run one-time setup (stores credentials in OS keyring)
python src/setup.py

# Alternative: Run selenium script directly
python Scripts/selenium_get_oauth.py
```

### Running the Server

```bash
# Start MCP server (stdio transport)
python src/server.py
```

### Testing

```bash
# Run unit tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Type checking
mypy src/
```

## MCP Configuration

Add to Kiro's `mcp.json` (use full path to venv Python):

```json
{
  "mcpServers": {
    "wlater": {
      "command": "C:/path/to/wlater-mcp/.venv/Scripts/python.exe",
      "args": ["C:/path/to/wlater-mcp/src/server.py"],
      "disabled": false
    }
  }
}
```

**Important**: Always use the virtual environment's Python executable, not the system Python.

## Authentication Flow

1. User runs `python src/setup.py` (one-time)
2. Selenium script automates Google login and extracts OAuth token
3. OAuth token exchanged for master token via gpsoauth
4. Master token stored in OS keyring
5. Config file (`.wlater`) created in home directory with email and android_id
6. Server reads credentials on startup and authenticates with gkeepapi

## Development Patterns

### FastMCP Tool Registration

Use the `@mcp.tool` decorator (no parentheses - FastMCP 2.7+ syntax):

```python
from fastmcp import FastMCP

mcp = FastMCP("wlater")

@mcp.tool
def list_all_notes() -> list:
    """List all notes from Google Keep (read-only)."""
    keep_client = get_keep_client()
    return keep_client.get_all_notes()
```

### Lazy Keep Client Initialization

```python
_keep_client = None

def get_keep_client():
    """Initialize Keep Client on first use."""
    global _keep_client
    if _keep_client is None:
        email, token, android_id = load_credentials()
        _keep_client = KeepClient(email, token, android_id)
    return _keep_client
```

### Error Handling

Let FastMCP handle exceptions - just raise with clear messages:

```python
@mcp.tool
def get_note(note_id: str) -> dict:
    keep_client = get_keep_client()
    note = keep_client.keep.get(note_id)
    
    if note is None:
        raise ValueError(f"Note {note_id} not found")
    
    return serialize_note(note)
```

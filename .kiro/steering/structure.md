# Project Structure and Organization

## Directory Layout

```
wlater-mcp/
├── .venv/                    # Virtual environment (DO NOT COMMIT)
├── .git/                     # Git repository
├── .kiro/                    # Kiro IDE configuration
│   ├── specs/               # Feature specifications (requirements, design, tasks)
│   └── steering/            # AI assistant guidance documents
├── src/                      # Source code (all Python modules)
│   ├── server.py            # Main MCP server entry point
│   ├── keep_client.py       # Google Keep API wrapper
│   ├── credentials.py       # Credential management (keyring + config file)
│   ├── tools.py             # MCP tool definitions
│   └── setup.py             # One-time credential setup script
├── Scripts/                  # User-facing utility scripts
│   └── selenium_get_oauth.py # Automated OAuth token retrieval
├── backup/                   # Legacy/backup scripts (not used in production)
├── Docs/                     # Documentation and design notes
│   ├── pathway.md           # Tiered exposure strategy
│   ├── exposed.md           # gkeepapi API reference
│   ├── android_id_proposal.md
│   └── alternatelinks.md
├── gkeepapi-main/           # Vendored gkeepapi library (reference)
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
└── README.md               # Project documentation
```

## File Responsibilities

### Core Server Files (src/)

- **`src/server.py`**: FastMCP application entry point. Registers tools and runs the MCP server using stdio transport.
- **`src/keep_client.py`**: Wrapper around gkeepapi. Handles authentication with `keep.resume()` and provides clean methods for note operations.
- **`src/credentials.py`**: Manages credential storage in OS keyring and `.wlater` config file. Provides validation and loading functions.
- **`src/tools.py`**: MCP tool definitions using `@mcp.tool` decorator. Each tool calls Keep Client methods and returns JSON-serializable data.

### Setup and Utilities

- **`src/setup.py`**: Interactive setup script. Offers selenium automation or manual credential entry. Stores credentials via `credentials.py`.
- **`Scripts/selenium_get_oauth.py`**: Automates Google login using Selenium WebDriver. Extracts OAuth token and exchanges for master token. Can be run standalone or imported by setup.py.

### Documentation

- **`Docs/pathway.md`**: Explains the tiered exposure strategy (Tier 1: read-only, Tier 2: modifications, Tier 3: destructive).
- **`Docs/exposed.md`**: Complete reference of gkeepapi API methods and properties.
- **`.kiro/specs/`**: Formal specifications for the MCP server feature (requirements, design, implementation tasks).

### Configuration Files

- **`.wlater`** (in user's home directory): JSON config file containing email, android_id, platform info, and preferences. Created by setup.py.
- **OS Keyring**: Stores master token securely using service name "wlater-mcp" and email as identifier.

## Architectural Layers

### Layer 1: MCP Protocol (FastMCP)
- Handles stdio transport
- Manages tool registration and invocation
- Formats responses and errors
- **Files**: `src/server.py`

### Layer 2: MCP Tools
- Exposes Keep operations as MCP tools
- Validates inputs and formats outputs
- Delegates to Keep Client
- **Files**: `src/tools.py`

### Layer 3: Keep Client
- Wraps gkeepapi library
- Manages authentication and sync
- Provides clean interface for note operations
- **Files**: `src/keep_client.py`

### Layer 4: Credential Management
- Stores/loads credentials from keyring and config
- Validates token and android_id formats
- Generates android_id deterministically
- **Files**: `src/credentials.py`

### Layer 5: External APIs
- gkeepapi library (Google Keep API)
- OS keyring (Windows Credential Locker, macOS Keychain, Linux Secret Service)

## Code Organization Principles

### Separation of Concerns
- **Server**: MCP protocol and tool registration
- **Tools**: Input validation and output formatting
- **Client**: Google Keep API interaction
- **Credentials**: Storage and retrieval

### Read-Only Enforcement
- No tools call `keep.sync()` to persist changes
- No tools expose create/update/delete operations
- Tool descriptions explicitly state read-only nature

### Error Handling
- Credential errors handled in `check_credentials` tool
- Authentication errors raised during lazy initialization
- Tool errors let FastMCP format exception responses
- All errors include clear user guidance

### State Management
- Keep Client stored in module-level variable (`_keep_client`)
- Lazy initialization on first tool invocation
- Client persists across tool calls within same server session

## Naming Conventions

### Files
- Snake case: `keep_client.py`, `selenium_get_oauth.py`
- Descriptive names indicating purpose

### Functions
- Snake case: `get_keep_client()`, `load_credentials()`
- Verb-noun pattern for actions: `store_credentials()`, `validate_master_token()`

### Classes
- Pascal case: `KeepClient`
- Noun-based names

### Constants
- Upper snake case: `SERVICE_NAME`, `PLATFORM_CODES`

### MCP Tools
- Snake case: `list_all_notes`, `get_note`, `search_notes`
- Action-oriented names matching their purpose

## Import Organization

Standard library imports first, then third-party, then local:

```python
import json
import logging
from pathlib import Path

import keyring
from fastmcp import FastMCP
import gkeepapi

from credentials import load_credentials
from keep_client import KeepClient
```

## Testing Structure

```
tests/
├── test_credentials.py       # Credential management tests
├── test_keep_client.py       # Keep Client tests (mocked gkeepapi)
├── test_tools.py             # MCP tool tests (mocked Keep Client)
├── test_setup_integration.py # Setup flow integration test
└── test_server_integration.py # Server startup integration test
```

All tests import from `src/` modules.

## Ignored Files (.gitignore)

- Virtual environments: `.venv/`, `venv/`, `env/`
- Python artifacts: `__pycache__/`, `*.pyc`, `*.egg-info/`
- Sensitive data: `master_token.txt`, `*.token`, `config.json`, `.env`, `.wlater/`
- IDE files: `.vscode/`, `.idea/`
- Vendored libraries: `gkeepapi-main/`
- Documentation drafts: `Docs/`, `backup/`

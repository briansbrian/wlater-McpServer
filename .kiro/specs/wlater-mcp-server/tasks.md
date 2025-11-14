# Implementation Plan

- [x] 1. Set up project structure and dependencies









  - Create project directory structure (credentials.py, keep_client.py, server.py, setup.py, selenium_get_oauth.py)
  - Create requirements.txt with fastmcp, gkeepapi, keyring, selenium dependencies
  - Create README.md with setup and usage instructions
  - _Requirements: 13.1_

- [x] 2. Implement credential management module





  - [x] 2.1 Implement credential storage functions

    - Write `store_credentials()` to save master token in keyring using `keyring.set_password("google-keep-token", email, master_token)`
    - Write `store_credentials()` to create `.wlater` config file in home directory with email, android_id, platform, username
    - _Requirements: 1.1, 2.1, 2.2_
  

  - [x] 2.2 Implement credential loading functions

    - Write `load_credentials()` to read `.wlater` config file from home directory
    - Write `load_credentials()` to retrieve master token from keyring using `keyring.get_password("google-keep-token", email)`
    - Handle FileNotFoundError for missing config and KeyringError for keyring access issues
    - _Requirements: 1.2, 2.3, 2.4_
  


  - [x] 2.3 Implement validation and Android ID generation functions

    - Write `validate_master_token()` to check token starts with "aas_et/"
    - Write `validate_android_id()` to check 16 hexadecimal character format
    - Write `generate_android_id()` to create deterministic 16-char hex ID using reversible base-36 encoding
    - Implement `encode_base36_to_hex()` to convert 6-char base-36 string to 8-char hex
    - Use structure: "776c61" (wlater) + platform_code + encoded_username
    - Normalize username: lowercase, alphanumeric only, first 6 chars, pad with '0'
    - _Requirements: 1.5, 2.5, 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7_


  
  - [x] 2.4 Implement platform detection and automatic regeneration

    - Write logic to detect platform/username changes in config
    - Implement android_id regeneration using deterministic base-36 encoding when platform or username differs
    - Update `.wlater` file with new android_id, platform, and username
    - Ensure regenerated ID is deterministic (same user + platform = same ID)
    - _Requirements: 2.6, 15.5_

- [x] 3. Implement Keep Client wrapper





  - [x] 3.1 Create KeepClient class with authentication

    - Initialize gkeepapi.Keep() instance
    - Implement `__init__()` to call `keep.resume(email, master_token, device_id=android_id)`
    - Perform initial sync with `keep.sync()`
    - Raise RuntimeError with clear message if authentication fails
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  

  - [x] 3.2 Implement note retrieval methods

    - Write `get_all_notes()` to call `keep.all()` and serialize notes
    - Return list with note_id, title, note_type, pinned, archived, color
    - Exclude trashed notes from results
    - Implement 1000 note limit with truncation indicator
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  

  - [x] 3.3 Implement note detail methods

    - Write `get_note()` to call `keep.get(note_id)` and serialize full note
    - Return dict with note_id, title, text, note_type, color, pinned, archived, labels, timestamps
    - Include ISO 8601 formatted timestamps (created, updated, edited)
    - Raise exception for non-existent note_id
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_


  

  - [x] 3.4 Implement list item methods

    - Write `get_list_items()` to verify note is List type
    - Extract and return all items, checked items, and unchecked items arrays
    - Include item_id, text, checked status, and sort order for each item
    - Return error message if note is not a List type


    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_

  
  - [x] 3.5 Implement search methods

    - Write `search_notes()` to call `keep.find()` with query
    - Support filters for pinned, archived, trashed, colors, and labels
    - Apply multiple filters using AND logic


    - Implement 100 result limit with truncation indicator

    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [x] 3.6 Implement label methods

    - Write `get_labels()` to call `keep.labels()` and return sorted list
    - Return label_id and name for each label
    - Sort labels alphabetically by name
    - Exclude deleted labels
    - Write `find_label()` to call `keep.findLabel()` with case-insensitive matching
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 10.1, 10.2, 10.3, 10.4, 10.5_

- [x] 4. Implement selenium authentication helper




  - [x] 4.1 Refactor selenium script for programmatic use


    - Add `run_selenium_auth()` function that wraps existing main() logic
    - Function should prompt for email and password
    - Generate android_id using deterministic `generate_android_id()` function with base-36 encoding
    - Extract oauth_token from cookies after authentication
    - Exchange oauth_token for master_token using gpsoauth
    - Return tuple: (email, master_token, android_id) on success, None on failure
    - Keep existing main() for standalone script usage
    - _Requirements: 3.2, 3.3, 15.1, 15.2, 15.3, 15.4_

- [x] 5. Implement setup script





  - [x] 5.1 Create interactive setup flow


    - Prompt user for selenium (s) or manual (m) credential entry
    - If selenium: import and call `run_selenium_auth()` from selenium_get_oauth module
    - Handle None return value (authentication failure) gracefully
    - If manual: prompt for email, master_token, and android_id
    - Validate master token format using `validate_master_token()`
    - Validate android_id format using `validate_android_id()`
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  
  - [x] 5.2 Implement credential storage

    - Call `store_credentials()` to save token in keyring and create `.wlater` file
    - Display success message with confirmation
    - Display next steps for configuring MCP server
    - _Requirements: 3.6, 3.7_

- [x] 6. Implement FastMCP server




  - [x] 6.1 Create FastMCP application instance



    - Initialize FastMCP with name "wlater"
    - Create module-level `_keep_client` variable for state
    - Write `get_keep_client()` helper for lazy initialization
    - _Requirements: 13.1, 14.1, 14.2, 14.3, 14.4_
  


  - [x] 6.2 Implement check_credentials tool

    - Create `@mcp.tool` decorated function `check_credentials()`
    - Call `load_credentials()` and return success dict with email
    - Catch and return error dict for FileNotFoundError, KeyringError, and other exceptions
    - Document as read-only in tool description
    - _Requirements: 12.5_


  

  - [x] 6.3 Implement list_all_notes tool

    - Create `@mcp.tool` decorated function `list_all_notes()`
    - Call `get_keep_client()` for lazy initialization
    - Call `keep_client.get_all_notes()` and return results
    - Document as read-only in tool description


    - _Requirements: 5.1, 5.2, 12.5, 13.2, 13.3_

  

  - [x] 6.4 Implement get_note tool

    - Create `@mcp.tool` decorated function `get_note(note_id: str)`
    - Call `get_keep_client()` for lazy initialization
    - Call `keep_client.get_note(note_id)` and return results
    - Raise ValueError for non-existent note_id
    - Document as read-only in tool description

    - _Requirements: 6.1, 6.2, 6.3, 12.5, 13.2, 13.3_



  

  - [x] 6.5 Implement get_list_items tool
    - Create `@mcp.tool` decorated function `get_list_items(list_id: str)`
    - Call `get_keep_client()` for lazy initialization
    - Call `keep_client.get_list_items(list_id)` and return results

    - Document as read-only in tool description

    - _Requirements: 7.1, 7.2, 7.3, 12.5, 13.2, 13.3_



  
  - [x] 6.6 Implement search_notes tool
    - Create `@mcp.tool` decorated function `search_notes()` with query and filter parameters
    - Call `get_keep_client()` for lazy initialization

    - Call `keep_client.search_notes()` with filters and return results

    - Document as read-only in tool description


    - _Requirements: 8.1, 8.2, 8.3, 12.5, 13.2, 13.3_

  
  - [x] 6.7 Implement label tools
    - Create `@mcp.tool` decorated function `list_labels()`
    - Create `@mcp.tool` decorated function `find_label(name: str)`

    - Call `get_keep_client()` for lazy initialization

    - Call respective keep_client methods and return results


    - Document as read-only in tool descriptions
    - _Requirements: 9.1, 10.1, 12.5, 13.2, 13.3_
  
  - [x] 6.8 Implement error handling and logging

    - Configure Python logging with INFO level

    - Log authentication success/failure


    - Log tool invocations
    - Let FastMCP handle exception formatting for tool errors
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 13.4_

  
  - [x] 6.9 Add server execution

    - Add `if __name__ == "__main__":` block
    - Call `mcp.run()` to start server with stdio transport
    - _Requirements: 13.5_

- [x] 7. Verify read-only enforcement





  - Review all tools to ensure no write/modify/delete operations
  - Verify no tools call `keep.sync()` to persist changes
  - Verify no tools expose createNote, createList, delete, trash, or deleteLabel
  - Verify no tools modify note properties (title, text, color, pinned, archived)
  - Confirm all tool descriptions document read-only nature
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [x] 8. Create documentation





  - Write README.md with installation instructions
  - Document virtual environment activation (`.venv\Scripts\activate` on Windows)
  - Document setup process (running `python setup.py` in venv)
  - Document MCP configuration for Kiro with full venv Python path
  - Document available tools and their parameters
  - Document troubleshooting steps
  - Include example MCP config with path: `C:/path/to/wlater-mcp/.venv/Scripts/python.exe`
  - Document Android ID generation algorithm including reversible base-36 encoding specification
  - Reference `Docs/android_id_proposal.md` for full Android ID specification
  - _Requirements: 3.7, 16.7_

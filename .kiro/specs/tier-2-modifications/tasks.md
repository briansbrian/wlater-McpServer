# Implementation Plan

**IMPORTANT**: Always use the virtual environment Python executable when running commands:
- Windows: `.venv\Scripts\python.exe`
- Linux/macOS: `.venv/bin/python`

This ensures all dependencies are correctly resolved from the virtual environment.

- [x] 1. Set up project structure and core interfaces




  - Extend KeepClient class in `src/keep_client.py` with modification method stubs
  - Add preview response formatting utilities
  - Add error handling helper functions
  - _Requirements: All_

- [x] 2. Implement list item operations




  - [x] 2.1 Implement `update_list_item_checked()` in KeepClient


    - Get list by ID using `keep.get()`
    - Find list item by iterating through `list.items`
    - Set `item.checked` property
    - Return preview with old and new checked status
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_
  
  - [x] 2.2 Implement `add_list_item()` in KeepClient


    - Get list by ID using `keep.get()`
    - Call `list.add(text, checked, sort)` to add item
    - Return preview with new item details
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x] 2.3 Add MCP tools for list operations in `src/server.py`


    - Register `update_list_item_checked` tool with `@mcp.tool`
    - Register `add_list_item` tool with `@mcp.tool`
    - Both tools call corresponding KeepClient methods
    - _Requirements: 1.1, 2.1_

- [x] 3. Implement note creation operations




  - [x] 3.1 Implement `create_note()` in KeepClient


    - Call `keep.createNote(title, text)`
    - Return preview with note ID, title, and text
    - _Requirements: 3.1, 3.2, 3.4, 3.5_
  
  - [x] 3.2 Implement `create_list()` in KeepClient


    - Format items as list of tuples: `[(text, checked), ...]`
    - Call `keep.createList(title, items)`
    - Return preview with list ID, title, and items
    - _Requirements: 3.1, 3.3, 3.4, 3.5_
  
  - [x] 3.3 Add MCP tools for note creation in `src/server.py`


    - Register `create_note` tool with `@mcp.tool`
    - Register `create_list` tool with `@mcp.tool`
    - Both tools call corresponding KeepClient methods
    - _Requirements: 3.1, 3.2, 3.3_

- [x] 4. Implement note update operations




  - [x] 4.1 Implement `update_note_title()` in KeepClient


    - Get note by ID using `keep.get()`
    - Store old title value
    - Set `note.title` property
    - Return preview with old and new title
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [x] 4.2 Implement `update_note_text()` in KeepClient


    - Get note by ID using `keep.get()`
    - Check if note is List type (raise error if true)
    - Store old text value
    - Set `note.text` property
    - Return preview with old and new text
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [x] 4.3 Add MCP tools for note updates in `src/server.py`


    - Register `update_note_title` tool with `@mcp.tool`
    - Register `update_note_text` tool with `@mcp.tool`
    - Both tools call corresponding KeepClient methods
    - _Requirements: 4.1, 4.2_

- [x] 5. Implement note property operations



  - [x] 5.1 Implement `update_note_color()` in KeepClient


    - Get note by ID using `keep.get()`
    - Map color string to `gkeepapi.node.ColorValue` enum
    - Set `note.color` property
    - Return preview with new color
    - _Requirements: 5.1, 5.4, 5.5_
  
  - [x] 5.2 Implement `update_note_pinned()` in KeepClient


    - Get note by ID using `keep.get()`
    - Set `note.pinned` property
    - Return preview with new pinned status
    - _Requirements: 5.2, 5.4_
  
  - [x] 5.3 Implement `update_note_archived()` in KeepClient


    - Get note by ID using `keep.get()`
    - Set `note.archived` property
    - Return preview with new archived status
    - _Requirements: 5.3, 5.4_
  
  - [x] 5.4 Add MCP tools for note properties in `src/server.py`


    - Register `update_note_color` tool with `@mcp.tool`
    - Register `update_note_pinned` tool with `@mcp.tool`
    - Register `update_note_archived` tool with `@mcp.tool`
    - All tools call corresponding KeepClient methods
    - _Requirements: 5.1, 5.2, 5.3_

- [x] 6. Implement label operations







  - [x] 6.1 Implement `create_label()` in KeepClient


    - Call `keep.createLabel(name)`
    - Return preview with label ID and name
    - _Requirements: 6.3, 6.4_
  
  - [x] 6.2 Implement `add_label_to_note()` in KeepClient


    - Get note by ID using `keep.get()`
    - Find label using `keep.findLabel(label_name)`
    - Call `note.labels.add(label)`
    - Return preview with note title and updated labels
    - _Requirements: 6.1, 6.4, 6.5_
  
  - [x] 6.3 Implement `remove_label_from_note()` in KeepClient


    - Get note by ID using `keep.get()`
    - Find label using `keep.findLabel(label_name)`
    - Call `note.labels.remove(label)`
    - Return preview with note title and updated labels
    - _Requirements: 6.2, 6.4, 6.5_
  
  - [x] 6.4 Add MCP tools for label operations in `src/server.py`


    - Register `create_label` tool with `@mcp.tool`
    - Register `add_label_to_note` tool with `@mcp.tool`
    - Register `remove_label_from_note` tool with `@mcp.tool`
    - All tools call corresponding KeepClient methods
    - _Requirements: 6.1, 6.2, 6.3_

- [x] 7. Implement sync control operations




  - [x] 7.1 Implement `sync_changes()` in KeepClient


    - Call `keep.sync()` to push all pending changes
    - Track number of changes synced (if possible)
    - Return confirmation with sync timestamp
    - _Requirements: 7.1, 7.3, 7.4, 7.5_
  
  - [x] 7.2 Implement `get_pending_changes()` in KeepClient


    - Iterate through all notes to find dirty/modified notes
    - Build list of changes with note IDs and change types
    - Return structured preview of all pending changes
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [x] 7.3 Implement `refresh_from_server()` in KeepClient


    - Call `keep.sync()` to fetch latest data and push pending changes
    - Return confirmation message
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_
  
  - [x] 7.4 Add MCP tools for sync control in `src/server.py`


    - Register `sync_changes` tool with `@mcp.tool`
    - Register `get_pending_changes` tool with `@mcp.tool`
    - Register `refresh_notes` tool with `@mcp.tool`
    - All tools call corresponding KeepClient methods
    - _Requirements: 7.1, 8.1, 9.1_

- [-] 8. Implement media access operations


  - [x] 8.1 Implement `get_note_media()` in KeepClient


    - Get note by ID using `keep.get()`
    - Access `note.images`, `note.drawings`, `note.audio`
    - Extract metadata (width, height, byte_size, extracted_text, length)
    - Return structured media information
    - _Requirements: 11.1, 11.3, 11.4_
  
  - [x] 8.2 Implement `get_media_link()` in KeepClient


    - Get note by ID using `keep.get()`
    - Find blob by ID in note.images, note.drawings, or note.audio
    - Call `keep.getMediaLink(blob)` to get download URL
    - Return URL with media metadata
    - _Requirements: 11.2, 11.3, 11.5_
  
  - [x] 8.3 Add MCP tools for media operations in `src/server.py`





    - Register `get_note_media` tool with `@mcp.tool`
    - Register `get_media_link` tool with `@mcp.tool`
    - Both tools call corresponding KeepClient methods
    - _Requirements: 11.1, 11.2_

- [x] 9. Implement trash operations (recoverable)








  - [x] 9.1 Implement `trash_note()` in KeepClient



    - Get note by ID using `keep.get()`
    - Store old trashed state
    - Call `note.trash()` to send note to trash
    - Return preview with old and new trashed status
    - _Requirements: Recoverable operation - notes can be restored_
  

  - [x] 9.2 Implement `untrash_note()` in KeepClient




    - Get note by ID using `keep.get()`
    - Store old trashed state
    - Call `note.untrash()` to restore note from trash
    - Return preview with old and new trashed status
    - _Requirements: Recoverable operation - restores trashed notes_
  

  - [x] 9.3 Add MCP tools for trash operations in `src/server.py`



    - Register `trash_note` tool with `@mcp.tool`
    - Register `untrash_note` tool with `@mcp.tool`
    - Both tools call corresponding KeepClient methods
    - Tool descriptions must emphasize recoverability

- [x] 10. Implement comprehensive error handling






  - [x] 9.1 Add validation error handling


    - Validate color names against ColorValue enum
    - Validate note/list/item IDs exist before operations
    - Return clear error messages with suggestions
    - _Requirements: 10.1, 10.5_
  

  - [x] 9.2 Add not found error handling



    - Handle cases where note/list/item/label not found
    - Return descriptive error messages
    - Include suggestions for finding resources
    - _Requirements: 10.2, 10.5_
  


  - [x] 9.3 Add type error handling


    - Check note type before text updates (List vs Note)
    - Return clear error messages explaining type mismatch
    - _Requirements: 10.1, 10.4_
  

  - [x] 9.4 Add API error handling




    - Wrap all gkeepapi calls in try-except blocks
    - Catch and format API exceptions
    - Return error details with context


    - _Requirements: 10.3, 10.4_

- [x] 11. Update documentation





  - Update README.md with Tier 2 capabilities overview
  - Document all new MCP tools with examples
  - Add safety guidelines for sync operations
  - Document the preview-before-sync workflow
  - _Requirements: All_

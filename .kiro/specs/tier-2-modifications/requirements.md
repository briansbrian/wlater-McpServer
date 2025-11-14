# Requirements Document

## Introduction

This specification defines Tier 2 modification capabilities for the wlater MCP server, enabling AI assistants to create and modify Google Keep notes with explicit user confirmation and manual sync control. This extends the existing read-only (Tier 1) functionality while maintaining strict safety boundaries to prevent accidental data loss.

## Glossary

- **Keep Client**: The KeepClient class that wraps gkeepapi and manages Google Keep API interactions
- **MCP Server**: The FastMCP-based Model Context Protocol server that exposes Keep operations as tools
- **Sync Operation**: The process of pushing local changes to Google Keep servers via `keep.sync()`
- **Modification Tool**: An MCP tool that creates or updates Keep data (notes, lists, labels)
- **User Confirmation**: Explicit approval required before executing any modification or sync operation
- **Preview**: A read-only representation of changes that will be applied if the user confirms
- **Pending Changes**: Local modifications that have not yet been synced to Google Keep servers

## Requirements

### Requirement 1

**User Story:** As a user, I want to check and uncheck todo items in my Google Keep lists through AI interactions, so that I can manage my tasks without switching to the Keep UI

#### Acceptance Criteria

1. WHEN the user requests to check a list item, THE Keep Client SHALL update the item's checked status to true
2. WHEN the user requests to uncheck a list item, THE Keep Client SHALL update the item's checked status to false
3. WHEN a list item's checked status is modified, THE MCP Server SHALL return a preview showing the item text and new status
4. WHERE the list item does not exist, THE MCP Server SHALL return an error message indicating the item was not found
5. WHILE changes are pending, THE Keep Client SHALL NOT automatically sync changes to Google Keep servers

### Requirement 2

**User Story:** As a user, I want to add new items to existing Google Keep lists through AI interactions, so that I can quickly capture tasks without manual entry

#### Acceptance Criteria

1. WHEN the user requests to add an item to a list, THE Keep Client SHALL create a new list item with the specified text
2. WHERE the user specifies a checked status, THE Keep Client SHALL set the item's checked property accordingly
3. WHERE the user does not specify a checked status, THE Keep Client SHALL default the item to unchecked
4. WHEN a new item is added, THE MCP Server SHALL return a preview showing the item text, checked status, and parent list title
5. WHERE the target list does not exist, THE MCP Server SHALL return an error message indicating the list was not found

### Requirement 3

**User Story:** As a user, I want to create new notes and lists through AI interactions, so that I can capture information quickly during conversations

#### Acceptance Criteria

1. WHEN the user requests to create a note, THE Keep Client SHALL create a new note with the specified title and text content
2. WHEN the user requests to create a list, THE Keep Client SHALL create a new list with the specified title and items
3. WHERE the user provides list items with checked status, THE Keep Client SHALL set each item's checked property accordingly
4. WHEN a new note or list is created, THE MCP Server SHALL return a preview showing the title, content, and note type
5. WHERE the title is empty, THE Keep Client SHALL create the note with an empty title string

### Requirement 4

**User Story:** As a user, I want to update note titles and content through AI interactions, so that I can refine my notes without manual editing

#### Acceptance Criteria

1. WHEN the user requests to update a note title, THE Keep Client SHALL set the note's title property to the new value
2. WHEN the user requests to update note text content, THE Keep Client SHALL set the note's text property to the new value
3. WHEN a note property is updated, THE MCP Server SHALL return a preview showing the old value and new value
4. WHERE the target note does not exist, THE MCP Server SHALL return an error message indicating the note was not found
5. WHERE the user attempts to update text on a list type note, THE MCP Server SHALL return an error indicating lists do not support text updates

### Requirement 5

**User Story:** As a user, I want to change note colors, pin status, and archive status through AI interactions, so that I can organize my notes efficiently

#### Acceptance Criteria

1. WHEN the user requests to change a note's color, THE Keep Client SHALL set the note's color property to the specified color value
2. WHEN the user requests to pin or unpin a note, THE Keep Client SHALL set the note's pinned property to the specified boolean value
3. WHEN the user requests to archive or unarchive a note, THE Keep Client SHALL set the note's archived property to the specified boolean value
4. WHEN a note status property is updated, THE MCP Server SHALL return a preview showing the property name and new value
5. WHERE an invalid color name is provided, THE MCP Server SHALL return an error message listing valid color options

### Requirement 6

**User Story:** As a user, I want to manage labels on my notes through AI interactions, so that I can categorize and organize my content

#### Acceptance Criteria

1. WHEN the user requests to add a label to a note, THE Keep Client SHALL add the specified label to the note's labels collection
2. WHEN the user requests to remove a label from a note, THE Keep Client SHALL remove the specified label from the note's labels collection
3. WHEN the user requests to create a new label, THE Keep Client SHALL create a label with the specified name
4. WHEN a label operation completes, THE MCP Server SHALL return a preview showing the note title and updated label list
5. WHERE a label does not exist when adding to a note, THE MCP Server SHALL return an error message indicating the label was not found

### Requirement 7

**User Story:** As a user, I want to explicitly review and approve all changes before they are synced to Google Keep, so that I can prevent accidental modifications

#### Acceptance Criteria

1. WHEN any modification tool is invoked, THE MCP Server SHALL NOT automatically sync changes to Google Keep servers
2. WHEN a modification is made, THE MCP Server SHALL return a preview of the change with a clear indication that sync is required
3. WHEN the user invokes the sync tool, THE Keep Client SHALL call keep.sync() to push all pending changes to Google Keep servers
4. WHEN sync completes successfully, THE MCP Server SHALL return a confirmation message indicating the number of changes synced
5. IF sync fails, THEN THE MCP Server SHALL return an error message with details about the failure

### Requirement 8

**User Story:** As a user, I want to see a preview of all pending changes before syncing, so that I can verify modifications are correct

#### Acceptance Criteria

1. WHEN the user requests to view pending changes, THE Keep Client SHALL retrieve all modified notes and lists
2. WHEN pending changes exist, THE MCP Server SHALL return a structured preview showing each modified item with change details
3. WHERE no pending changes exist, THE MCP Server SHALL return a message indicating there are no changes to sync
4. WHEN displaying previews, THE MCP Server SHALL include note titles, change types, and affected properties
5. WHILE displaying previews, THE MCP Server SHALL NOT modify any data or trigger sync operations

### Requirement 9

**User Story:** As a user, I want the ability to refresh the Keep client's cache to see new notes created outside the MCP server, so that I have access to my latest data

#### Acceptance Criteria

1. WHEN the user invokes the refresh tool, THE Keep Client SHALL call keep.sync() to fetch the latest data from Google Keep servers
2. WHEN refresh completes successfully, THE MCP Server SHALL return a confirmation message indicating the cache was updated
3. WHEN refresh is invoked with pending local changes, THE Keep Client SHALL push those changes to the server during sync
4. IF refresh fails, THEN THE MCP Server SHALL return an error message with details about the failure
5. WHILE refresh is in progress, THE Keep Client SHALL update its internal cache with all notes, lists, and labels from the server

### Requirement 10

**User Story:** As a user, I want clear error messages when modification operations fail, so that I can understand what went wrong and how to fix it

#### Acceptance Criteria

1. WHERE a modification tool receives invalid input, THE MCP Server SHALL return an error message describing the validation failure
2. WHERE a note or list ID does not exist, THE MCP Server SHALL return an error message indicating the resource was not found
3. WHERE a modification operation fails due to API errors, THE MCP Server SHALL return an error message with the underlying error details
4. WHEN an error occurs, THE MCP Server SHALL NOT modify any data or leave the system in an inconsistent state
5. WHERE appropriate, THE MCP Server SHALL include suggestions for correcting the error in the error message

### Requirement 11

**User Story:** As a user, I want to access media attachments (images, drawings, audio) from my notes through AI interactions, so that I can retrieve and reference media content

#### Acceptance Criteria

1. WHEN the user requests media from a note, THE Keep Client SHALL retrieve all media blobs attached to the note
2. WHEN the user requests a media link, THE Keep Client SHALL call the Media API to get the canonical download URL
3. WHEN media is retrieved, THE MCP Server SHALL return metadata including media type, dimensions, and extracted text where available
4. WHERE a note has no media attachments, THE MCP Server SHALL return an empty list
5. WHERE media extraction fails, THE MCP Server SHALL return an error message with details about the failure

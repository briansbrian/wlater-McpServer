# Requirements Document

## Introduction

The wlater MCP (Model Context Protocol) server provides AI assistants with secure, read-only access to Google Keep notes and lists. The system enables users to query, search, and analyze their Keep data through natural language interactions while maintaining strict security boundaries. The server implements Tier 1 (read-only) operations only, preventing any destructive or modification actions that could result in data loss. The server is built using FastMCP, a Python framework that simplifies MCP server development with decorators and automatic tool registration.

## Glossary

- **MCP Server**: A service implementing the Model Context Protocol that exposes tools for AI assistants to interact with Google Keep data
- **FastMCP**: A Python framework for building MCP servers using decorators and automatic tool registration
- **FastMCP Application**: An instance of the FastMCP class that manages tool registration, lifecycle, and server execution
- **Tool Decorator**: The @mcp.tool() decorator provided by FastMCP that registers Python functions as MCP tools
- **Keep Client**: A wrapper around the gkeepapi library that manages authentication and API interactions with Google Keep
- **Master Token**: A long-lived OAuth token (format: `aas_et/...`) used to authenticate with Google Keep API
- **Android ID**: A 16-character hexadecimal identifier required for Google Keep API authentication, generated using reversible base-36 encoding from system username and platform
- **Keyring**: An OS-native credential storage system (Windows Credential Locker, macOS Keychain, Linux Secret Service)
- **Config File**: A JSON file (`.wlater`) storing non-sensitive configuration data such as email and preferences
- **Note**: A Google Keep note containing title and text content
- **List**: A Google Keep list containing checkable items
- **Label**: A tag that can be applied to notes and lists for organization
- **Tier 1 Operations**: Read-only operations that cannot modify or delete data

## Requirements

### Requirement 1

**User Story:** As a user, I want to securely store my Google Keep credentials using OS-native storage, so that my master token is protected and not exposed in plaintext files.

#### Acceptance Criteria

1. WHEN the user runs the credential setup process, THE MCP Server SHALL store the master token in the system keyring using the service name "wlater-mcp" and the user's email as the identifier
2. WHEN the MCP Server starts, THE MCP Server SHALL retrieve the master token from the system keyring using the stored email address
3. IF the master token is not found in the keyring, THEN THE MCP Server SHALL fail gracefully with a clear error message instructing the user to run the setup process
4. THE MCP Server SHALL support keyring backends for Windows Credential Locker, macOS Keychain, and Linux Secret Service
5. WHEN storing credentials, THE MCP Server SHALL validate that the master token follows the expected format (starts with "aas_et/")

### Requirement 2

**User Story:** As a user, I want to store non-sensitive configuration in a local file, so that I can manage preferences and settings without exposing sensitive data.

#### Acceptance Criteria

1. WHEN the setup process completes, THE MCP Server SHALL create a `.wlater` configuration file in the user's home directory containing email, android_id, android_id_platform, android_id_username, and preferences
2. THE Config File SHALL be formatted as valid JSON with fields for email, android_id, android_id_platform, android_id_username, last_sync timestamp, and preferences object
3. WHEN the MCP Server starts, THE MCP Server SHALL read the `.wlater` configuration file from the home directory to obtain the email address for keyring lookup
4. IF the `.wlater` file does not exist, THEN THE MCP Server SHALL fail gracefully with instructions to run the setup process
5. THE MCP Server SHALL validate that the android_id in the config file is exactly 16 hexadecimal characters
6. WHEN the MCP Server detects that android_id_platform or android_id_username differs from the current system, THE MCP Server SHALL regenerate the android_id using deterministic base-36 encoding and update the config file

### Requirement 3

**User Story:** As a user, I want a simple setup process that guides me through credential storage, so that I can quickly configure the MCP server without manual keyring manipulation.

#### Acceptance Criteria

1. WHEN the user runs the setup script, THE Setup Script SHALL prompt for the user's Google email address
2. WHEN the user provides an email, THE Setup Script SHALL offer to run the selenium authentication script or accept manually obtained credentials
3. IF the user chooses selenium, THE Setup Script SHALL call the selenium module which returns email, master_token, and android_id
4. IF the user chooses manual entry, THE Setup Script SHALL prompt for email, master_token, and android_id
5. WHEN credentials are provided, THE Setup Script SHALL validate the master token format and android_id format before storing
6. WHEN credentials are validated, THE Setup Script SHALL store the master token in keyring and create the `.wlater` config file
7. WHEN setup completes successfully, THE Setup Script SHALL display a confirmation message with next steps for running the MCP server

### Requirement 4

**User Story:** As a user, I want the MCP server to authenticate with Google Keep using my stored credentials, so that AI assistants can access my notes without repeated login prompts.

#### Acceptance Criteria

1. WHEN the MCP Server starts, THE Keep Client SHALL retrieve the master token from keyring and email from the config file
2. WHEN credentials are retrieved, THE Keep Client SHALL authenticate with the gkeepapi library using the email, master token, and android_id
3. IF authentication fails, THEN THE Keep Client SHALL log the error and terminate with a clear message indicating credential issues
4. WHEN authentication succeeds, THE Keep Client SHALL perform an initial sync to retrieve all notes from Google Keep
5. THE Keep Client SHALL maintain the authenticated session for the lifetime of the MCP Server process

### Requirement 5

**User Story:** As an AI assistant, I want to list all notes and lists from Google Keep, so that I can provide users with an overview of their content.

#### Acceptance Criteria

1. WHEN the list_all_notes tool is invoked, THE MCP Server SHALL retrieve the Keep Client from FastMCP context and call the gkeepapi all() method
2. WHEN notes are retrieved, THE MCP Server SHALL return a JSON-serializable list containing note_id, title, note_type (Note or List), pinned status, archived status, and color for each note
3. THE MCP Server SHALL exclude trashed notes from the list_all_notes results
4. WHEN a note has no title, THE MCP Server SHALL return an empty string for the title field
5. THE MCP Server SHALL limit results to 1000 notes and include a truncation indicator if more notes exist

### Requirement 6

**User Story:** As an AI assistant, I want to retrieve detailed content for a specific note by ID, so that I can answer questions about individual notes.

#### Acceptance Criteria

1. WHEN the get_note tool is invoked with a note_id parameter, THE MCP Server SHALL retrieve the Keep Client from FastMCP context and call the gkeepapi get() method
2. WHEN the note is found, THE MCP Server SHALL return a JSON-serializable dictionary containing note_id, title, text, note_type, color, pinned, archived, labels, and timestamps
3. IF the note_id does not exist, THEN THE MCP Server SHALL raise an exception that FastMCP will format as an error response
4. WHEN the note is a List type, THE MCP Server SHALL include the text field containing the serialized list content
5. THE MCP Server SHALL include created, updated, and edited timestamps in ISO 8601 format

### Requirement 7

**User Story:** As an AI assistant, I want to retrieve list items with their checked status, so that I can report on todo completion and pending tasks.

#### Acceptance Criteria

1. WHEN the get_list_items tool is invoked with a list_id parameter, THE MCP Server SHALL verify the note is a List type
2. WHEN the note is a List, THE MCP Server SHALL return JSON containing arrays for all items, checked items, and unchecked items
3. WHEN returning list items, THE MCP Server SHALL include item_id, text, checked status, and sort order for each item
4. IF the note_id is not a List type, THEN THE MCP Server SHALL return an error message indicating the note is not a list
5. THE MCP Server SHALL return items in their display order based on sort values

### Requirement 8

**User Story:** As an AI assistant, I want to search notes by query text and filters, so that I can find specific notes matching user criteria.

#### Acceptance Criteria

1. WHEN the search_notes tool is invoked with a query parameter, THE MCP Server SHALL call the Keep Client to search using gkeepapi find() method
2. WHEN search filters are provided, THE MCP Server SHALL support filtering by pinned status, archived status, trashed status, colors, and labels
3. WHEN multiple filters are provided, THE MCP Server SHALL apply all filters using AND logic
4. WHEN search results are returned, THE MCP Server SHALL include the same fields as list_all_notes for each matching note
5. THE MCP Server SHALL limit search results to 100 notes and include a truncation indicator if more matches exist

### Requirement 9

**User Story:** As an AI assistant, I want to list all available labels, so that I can help users filter and organize their notes by labels.

#### Acceptance Criteria

1. WHEN the list_labels tool is invoked, THE MCP Server SHALL call the Keep Client to retrieve all labels using gkeepapi labels() method
2. WHEN labels are retrieved, THE MCP Server SHALL return a JSON array containing label_id and name for each label
3. THE MCP Server SHALL return labels in alphabetical order by name
4. WHEN no labels exist, THE MCP Server SHALL return an empty array
5. THE MCP Server SHALL exclude deleted labels from the results

### Requirement 10

**User Story:** As an AI assistant, I want to find a label by name, so that I can use it to filter notes in search operations.

#### Acceptance Criteria

1. WHEN the find_label tool is invoked with a name parameter, THE MCP Server SHALL call the Keep Client to search using gkeepapi findLabel() method
2. WHEN a matching label is found, THE MCP Server SHALL return JSON containing label_id and name
3. IF no matching label is found, THEN THE MCP Server SHALL return null
4. THE MCP Server SHALL perform case-insensitive matching on label names
5. WHEN multiple labels match, THE MCP Server SHALL return the first match

### Requirement 11

**User Story:** As a developer, I want the MCP server to implement proper error handling, so that failures are logged clearly and don't crash the server.

#### Acceptance Criteria

1. WHEN any tool encounters an error, THE MCP Server SHALL allow FastMCP to catch the exception and format it as a structured error response
2. WHEN an error occurs, THE MCP Server SHALL use Python logging to record the error with timestamp, tool name, and error details
3. THE FastMCP Application SHALL continue running after handling tool errors without terminating the process
4. WHEN authentication fails, THE MCP Server SHALL raise an exception with specific guidance on credential issues
5. WHEN network errors occur, THE MCP Server SHALL raise an exception with a message indicating connectivity issues with Google Keep

### Requirement 12

**User Story:** As a user, I want the MCP server to enforce read-only operations, so that AI assistants cannot accidentally modify or delete my notes.

#### Acceptance Criteria

1. THE MCP Server SHALL NOT expose any tools that call gkeepapi methods for creating, modifying, or deleting notes
2. THE MCP Server SHALL NOT expose the sync() method that would persist changes to Google Keep
3. THE MCP Server SHALL NOT expose tools for createNote, createList, delete, trash, or deleteLabel operations
4. THE MCP Server SHALL NOT expose tools for modifying note properties such as title, text, color, pinned, or archived
5. THE MCP Server SHALL document in tool descriptions that all operations are read-only

### Requirement 13

**User Story:** As a developer, I want to use FastMCP to build the MCP server, so that I can leverage its simplified API and automatic tool registration instead of manually implementing the MCP protocol.

#### Acceptance Criteria

1. THE MCP Server SHALL create a FastMCP Application instance using the FastMCP class constructor with the server name "wlater"
2. WHEN defining MCP tools, THE MCP Server SHALL use the @mcp.tool() decorator to register Python functions as tools
3. WHEN the server starts, THE FastMCP Application SHALL automatically register all decorated functions as available MCP tools
4. THE MCP Server SHALL use FastMCP's built-in error handling and response formatting for all tool invocations
5. WHEN the server is executed, THE MCP Server SHALL call the FastMCP run() method to start the server using stdio transport

### Requirement 14

**User Story:** As a developer, I want to initialize the Keep Client on first use, so that authentication happens only when needed and the client is available for all subsequent tool invocations.

#### Acceptance Criteria

1. WHEN any tool requiring Keep access is invoked, THE MCP Server SHALL check if a Keep Client exists in the server's state
2. IF the Keep Client does not exist, THE MCP Server SHALL retrieve credentials from keyring and config file
3. WHEN credentials are retrieved, THE MCP Server SHALL create and authenticate the Keep Client instance
4. WHEN authentication succeeds, THE MCP Server SHALL store the Keep Client in the server's state for reuse by subsequent tool invocations
5. IF authentication fails, THEN THE MCP Server SHALL raise an exception with guidance to run the setup script

### Requirement 15

**User Story:** As a security administrator, I want Android IDs to be generated using a reversible base-36 encoding algorithm, so that I can decode usernames during breach investigations while maintaining deterministic ID generation.

#### Acceptance Criteria

1. WHEN generating an Android ID, THE MCP Server SHALL use the structure "776c61" (wlater prefix) + platform_code + encoded_username to create a 16-character hexadecimal identifier
2. WHEN detecting the platform, THE MCP Server SHALL map the system platform to a 2-character hexadecimal code (01=Windows, 02=Linux, 03=Darwin/macOS, 00=Unknown)
3. WHEN normalizing the username, THE MCP Server SHALL take the first 8 characters, convert to lowercase, keep only alphanumeric characters, truncate to 6 characters, and pad with '0' if less than 6 characters
4. WHEN encoding the username, THE MCP Server SHALL convert the 6-character base-36 string to an 8-character hexadecimal string using base-36 to integer to hexadecimal conversion
5. THE MCP Server SHALL generate the same Android ID for the same username and platform combination (deterministic behavior)
6. THE Android ID generation algorithm SHALL be reversible, allowing decoding of the username from the 8-character hex segment for breach investigation purposes
7. THE MCP Server SHALL validate that generated Android IDs are exactly 16 hexadecimal characters before storing in the config file

### Requirement 16

**User Story:** As a user, I want the MCP server to run using the project's virtual environment, so that all dependencies are isolated and the correct versions are used.

#### Acceptance Criteria

1. WHEN the MCP Server is configured in Kiro, THE MCP Configuration SHALL specify the full path to the virtual environment's Python executable
2. THE MCP Configuration SHALL use the path `.venv/Scripts/python.exe` on Windows or `.venv/bin/python` on Linux/macOS
3. THE MCP Configuration SHALL specify the server entry point as `src/server.py`
4. WHEN setup scripts are run, THE User SHALL activate the virtual environment before running Python commands
5. THE Documentation SHALL include instructions for activating the virtual environment on different platforms
6. THE Documentation SHALL include the correct MCP configuration with full venv Python path and src/ folder structure
7. THE Documentation SHALL document the Android ID generation algorithm including the reversible base-36 encoding specification

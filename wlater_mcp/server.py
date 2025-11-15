"""wlater MCP Server - Read-only Google Keep access for AI assistants.

This server provides MCP tools for querying, searching, and retrieving
Google Keep notes and lists without any modification capabilities.
"""

import logging
from typing import List, Optional, Dict, Any

try:
    from fastmcp import FastMCP
except ImportError:
    raise ImportError(
        "fastmcp is required. Install it with: pip install fastmcp"
    )

from wlater_mcp.credentials import load_credentials
from wlater_mcp.keep_client import KeepClient


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("wlater")

# Initialize FastMCP application
mcp = FastMCP("wlater")

# Module-level state for Keep Client (persists across tool calls)
_keep_client: Optional[KeepClient] = None


def get_keep_client() -> KeepClient:
    """Lazy initialization of Keep Client on first use.
    
    Returns:
        Authenticated KeepClient instance
        
    Raises:
        RuntimeError: If authentication fails
    """
    global _keep_client
    
    if _keep_client is None:
        try:
            email, token, android_id = load_credentials()
            _keep_client = KeepClient(email, token, android_id)
            logger.info("Keep Client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Keep Client: {e}")
            raise RuntimeError(
                f"Authentication failed: {e}. "
                "Run check_credentials tool for details or re-run setup.py"
            )
    
    return _keep_client


@mcp.tool
def check_credentials() -> Dict[str, Any]:
    """Check if credentials are configured and valid (read-only).
    
    Returns:
        Dictionary with configuration status and email if configured
    """
    try:
        email, token, android_id = load_credentials()
        return {
            "configured": True,
            "email": email,
            "message": "Credentials found and valid"
        }
    except FileNotFoundError as e:
        return {
            "configured": False,
            "message": f"Config file not found: {e}. Run setup.py first."
        }
    except Exception as e:
        return {
            "configured": False,
            "message": f"Error loading credentials: {e}"
        }


@mcp.tool
def list_all_notes() -> List[Dict[str, Any]]:
    """List all notes and lists from Google Keep (read-only).
    
    Returns:
        List of note dictionaries with basic metadata
    """
    keep_client = get_keep_client()
    return keep_client.get_all_notes()


@mcp.tool
def get_note(note_id: str) -> Dict[str, Any]:
    """Get detailed content for a specific note by ID (read-only).
    
    Args:
        note_id: Google Keep note ID
        
    Returns:
        Dictionary with full note details including text, labels, and timestamps
    """
    keep_client = get_keep_client()
    return keep_client.get_note(note_id)


@mcp.tool
def get_list_items(list_id: str) -> Dict[str, Any]:
    """Get list items with checked status (read-only).
    
    Args:
        list_id: Google Keep list ID
        
    Returns:
        Dictionary with all items, checked items, and unchecked items
    """
    keep_client = get_keep_client()
    return keep_client.get_list_items(list_id)


@mcp.tool
def search_notes(
    query: Optional[str] = None,
    pinned: Optional[bool] = None,
    archived: Optional[bool] = None,
    trashed: Optional[bool] = None,
    colors: Optional[List[str]] = None,
    labels: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """Search notes with optional filters (read-only).
    
    Args:
        query: Text to search for in notes
        pinned: Filter by pinned status
        archived: Filter by archived status
        trashed: Filter by trashed status
        colors: Filter by color names (e.g., ["RED", "BLUE"])
        labels: Filter by label names
        
    Returns:
        List of matching note dictionaries
    """
    keep_client = get_keep_client()
    return keep_client.search_notes(
        query=query,
        pinned=pinned,
        archived=archived,
        trashed=trashed,
        colors=colors,
        labels=labels
    )


@mcp.tool
def list_labels() -> List[Dict[str, str]]:
    """List all labels sorted alphabetically (read-only).
    
    Returns:
        List of label dictionaries with id and name
    """
    keep_client = get_keep_client()
    return keep_client.get_labels()


@mcp.tool
def find_label(name: str) -> Optional[Dict[str, str]]:
    """Find a label by name with case-insensitive matching (read-only).
    
    Args:
        name: Label name to search for
        
    Returns:
        Label dictionary or None if not found
    """
    keep_client = get_keep_client()
    return keep_client.find_label(name)


# ============================================================================
# TIER 2: MODIFICATION TOOLS (Require explicit sync)
# ============================================================================

@mcp.tool
def update_list_item_checked(
    list_id: str, 
    item_id: str, 
    checked: bool
) -> Dict[str, Any]:
    """Update checked status of a list item (requires sync).
    
    Changes are made locally and must be synced with sync_changes().
    
    Args:
        list_id: Google Keep list ID
        item_id: List item ID
        checked: New checked status (True to check, False to uncheck)
        
    Returns:
        Preview response showing old and new checked status
    """
    keep_client = get_keep_client()
    return keep_client.update_list_item_checked(list_id, item_id, checked)


@mcp.tool
def add_list_item(
    list_id: str, 
    text: str, 
    checked: bool = False,
    sort: int = None
) -> Dict[str, Any]:
    """Add new item to existing list (requires sync).
    
    Changes are made locally and must be synced with sync_changes().
    
    Args:
        list_id: Google Keep list ID
        text: Item text
        checked: Initial checked status (default: False)
        sort: Sort order (optional)
        
    Returns:
        Preview response with new item details
    """
    keep_client = get_keep_client()
    return keep_client.add_list_item(list_id, text, checked, sort)


@mcp.tool
def create_note(
    title: str = "", 
    text: str = ""
) -> Dict[str, Any]:
    """Create new text note (requires sync).
    
    Creates a new note locally. Must call sync_changes() to save to Google Keep.
    
    Args:
        title: Note title (default: empty)
        text: Note text content (default: empty)
        
    Returns:
        Preview response with note ID, title, and text
    """
    keep_client = get_keep_client()
    return keep_client.create_note(title, text)


@mcp.tool
def create_list(
    title: str = "", 
    items: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create new list with items (requires sync).
    
    Items format: [{"text": "item text", "checked": False}, ...]
    Must call sync_changes() to save to Google Keep.
    
    Args:
        title: List title (default: empty)
        items: List of items with format [{"text": "...", "checked": False}, ...]
        
    Returns:
        Preview response with list ID, title, and items
    """
    keep_client = get_keep_client()
    return keep_client.create_list(title, items)


@mcp.tool
def update_note_title(
    note_id: str, 
    title: str
) -> Dict[str, Any]:
    """Update note title (requires sync).
    
    Changes are made locally and must be synced with sync_changes().
    
    Args:
        note_id: Google Keep note ID
        title: New title
        
    Returns:
        Preview response showing old and new title
    """
    keep_client = get_keep_client()
    return keep_client.update_note_title(note_id, title)


@mcp.tool
def update_note_text(
    note_id: str, 
    text: str
) -> Dict[str, Any]:
    """Update note text content (requires sync).
    
    Changes are made locally and must be synced with sync_changes().
    Note: Only works on Note type, not List type.
    
    Args:
        note_id: Google Keep note ID
        text: New text content
        
    Returns:
        Preview response showing old and new text
    """
    keep_client = get_keep_client()
    return keep_client.update_note_text(note_id, text)


@mcp.tool
def update_note_color(
    note_id: str, 
    color: str
) -> Dict[str, Any]:
    """Update note color (requires sync).
    
    Changes are made locally and must be synced with sync_changes().
    
    Args:
        note_id: Google Keep note ID
        color: Color name (White, Red, Orange, Yellow, Green, Teal, 
               Blue, DarkBlue, Purple, Pink, Brown, Gray)
        
    Returns:
        Preview response showing old and new color
    """
    keep_client = get_keep_client()
    return keep_client.update_note_color(note_id, color)


@mcp.tool
def update_note_pinned(
    note_id: str, 
    pinned: bool
) -> Dict[str, Any]:
    """Pin or unpin note (requires sync).
    
    Changes are made locally and must be synced with sync_changes().
    
    Args:
        note_id: Google Keep note ID
        pinned: New pinned status (True to pin, False to unpin)
        
    Returns:
        Preview response showing old and new pinned status
    """
    keep_client = get_keep_client()
    return keep_client.update_note_pinned(note_id, pinned)


@mcp.tool
def update_note_archived(
    note_id: str, 
    archived: bool
) -> Dict[str, Any]:
    """Archive or unarchive note (requires sync).
    
    Changes are made locally and must be synced with sync_changes().
    
    Args:
        note_id: Google Keep note ID
        archived: New archived status (True to archive, False to unarchive)
        
    Returns:
        Preview response showing old and new archived status
    """
    keep_client = get_keep_client()
    return keep_client.update_note_archived(note_id, archived)


@mcp.tool
def create_label(name: str) -> Dict[str, Any]:
    """Create new label (requires sync).
    
    Creates a new label locally. Must call sync_changes() to save to Google Keep.
    
    Args:
        name: Label name
        
    Returns:
        Preview response with label ID and name
    """
    keep_client = get_keep_client()
    return keep_client.create_label(name)


@mcp.tool
def add_label_to_note(
    note_id: str, 
    label_name: str
) -> Dict[str, Any]:
    """Add label to note (requires sync).
    
    Changes are made locally and must be synced with sync_changes().
    
    Args:
        note_id: Google Keep note ID
        label_name: Label name to add
        
    Returns:
        Preview response with note title and updated labels
    """
    keep_client = get_keep_client()
    return keep_client.add_label_to_note(note_id, label_name)


@mcp.tool
def remove_label_from_note(
    note_id: str, 
    label_name: str
) -> Dict[str, Any]:
    """Remove label from note (requires sync).
    
    Changes are made locally and must be synced with sync_changes().
    
    Args:
        note_id: Google Keep note ID
        label_name: Label name to remove
        
    Returns:
        Preview response with note title and updated labels
    """
    keep_client = get_keep_client()
    return keep_client.remove_label_from_note(note_id, label_name)


# ============================================================================
# SYNC CONTROL TOOLS
# ============================================================================

@mcp.tool
def sync_changes() -> Dict[str, Any]:
    """Sync all pending changes to Google Keep.
    
    Pushes all local modifications to Google Keep servers.
    This is the ONLY way changes are saved.
    
    Returns:
        Confirmation with sync timestamp
    """
    keep_client = get_keep_client()
    return keep_client.sync_changes()


@mcp.tool
def get_pending_changes() -> Dict[str, Any]:
    """Get preview of all pending changes before syncing.
    
    Shows what will be synced when sync_changes() is called.
    
    Returns:
        Structured preview of all pending changes
    """
    keep_client = get_keep_client()
    return keep_client.get_pending_changes()


@mcp.tool
def refresh_notes() -> Dict[str, Any]:
    """Refresh local cache from Google Keep server.
    
    Fetches latest data from Google Keep. If there are pending local
    changes, they will be synced during this operation.
    
    Returns:
        Confirmation message with timestamp
    """
    keep_client = get_keep_client()
    return keep_client.refresh_from_server()


# ============================================================================
# MEDIA OPERATIONS (Read-Only)
# ============================================================================

@mcp.tool
def get_note_media(note_id: str) -> Dict[str, Any]:
    """Get all media attachments from a note (read-only).
    
    Returns metadata for images, drawings, and audio clips attached to a note.
    
    Args:
        note_id: Google Keep note ID
        
    Returns:
        Dictionary with media metadata including type, dimensions, and extracted text
    """
    keep_client = get_keep_client()
    return keep_client.get_note_media(note_id)


@mcp.tool
def get_media_link(note_id: str, blob_id: str) -> Dict[str, Any]:
    """Get download URL for a media blob (read-only).
    
    Returns canonical URL for downloading the media file. Note that URLs
    are temporary and may expire.
    
    Args:
        note_id: Google Keep note ID
        blob_id: Media blob ID (from get_note_media)
        
    Returns:
        Dictionary with download URL and media metadata
    """
    keep_client = get_keep_client()
    return keep_client.get_media_link(note_id, blob_id)


# ============================================================================
# TRASH OPERATIONS (Recoverable)
# ============================================================================

@mcp.tool
def trash_note(note_id: str) -> Dict[str, Any]:
    """Move note to trash (requires sync, recoverable operation).
    
    This is a RECOVERABLE operation - trashed notes can be restored using
    untrash_note(). Changes are made locally and must be synced with sync_changes().
    
    Args:
        note_id: Google Keep note ID
        
    Returns:
        Preview response showing old and new trashed status
    """
    keep_client = get_keep_client()
    return keep_client.trash_note(note_id)


@mcp.tool
def untrash_note(note_id: str) -> Dict[str, Any]:
    """Restore note from trash (requires sync, recoverable operation).
    
    This RESTORES a trashed note back to active status. Changes are made
    locally and must be synced with sync_changes().
    
    Args:
        note_id: Google Keep note ID
        
    Returns:
        Preview response showing old and new trashed status
    """
    keep_client = get_keep_client()
    return keep_client.untrash_note(note_id)


if __name__ == "__main__":
    logger.info("Starting wlater MCP server...")
    mcp.run()

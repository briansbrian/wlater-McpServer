"""wlater MCP Server - Read-only Google Keep access for AI assistants.

This server provides MCP tools for querying, searching, and retrieving
Google Keep notes and lists without any modification capabilities.
"""

import logging
from typing import List, Optional, Dict, Any

from fastmcp import FastMCP

from credentials import load_credentials
from keep_client import KeepClient


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


if __name__ == "__main__":
    logger.info("Starting wlater MCP server...")
    mcp.run()

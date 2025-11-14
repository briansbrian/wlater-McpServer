"""Google Keep client wrapper for read-only and modification operations."""

import logging
import re
from datetime import datetime
from typing import List, Dict, Optional, Any

import gkeepapi


logger = logging.getLogger("wlater")


# Preview Response Formatting Utilities

def format_preview_response(
    operation: str,
    preview: Dict[str, Any],
    message: str = None
) -> Dict[str, Any]:
    """Format a standard preview response for modification operations.
    
    Args:
        operation: Name of the operation (e.g., "update_list_item_checked")
        preview: Dictionary containing preview details
        message: Optional custom message
        
    Returns:
        Standardized preview response dictionary
    """
    default_message = f"Updated locally. Call sync_changes() to save to Google Keep."
    
    return {
        "success": True,
        "operation": operation,
        "preview": preview,
        "synced": False,
        "message": message or default_message
    }


def format_sync_response(
    changes_synced: int,
    timestamp: str = None
) -> Dict[str, Any]:
    """Format a standard sync response.
    
    Args:
        changes_synced: Number of changes synced
        timestamp: ISO timestamp of sync (defaults to current time)
        
    Returns:
        Standardized sync response dictionary
    """
    if timestamp is None:
        timestamp = datetime.utcnow().isoformat() + "Z"
    
    return {
        "success": True,
        "operation": "sync",
        "changes_synced": changes_synced,
        "timestamp": timestamp,
        "message": f"Successfully synced {changes_synced} changes to Google Keep"
    }


def format_error_response(
    error_type: str,
    message: str,
    suggestion: Optional[str] = None
) -> Dict[str, Any]:
    """Format a standard error response.
    
    Args:
        error_type: Type of error (e.g., "ValueError", "TypeError")
        message: Error message
        suggestion: Optional suggestion for fixing the error
        
    Returns:
        Standardized error response dictionary
    """
    return {
        "success": False,
        "error": error_type,
        "message": message,
        "suggestion": suggestion
    }


# Error Handling Helper Functions

def validate_note_exists(keep: gkeepapi.Keep, note_id: str) -> Optional[Dict[str, Any]]:
    """Validate that a note exists.
    
    Args:
        keep: gkeepapi Keep instance
        note_id: Note ID to validate
        
    Returns:
        Error response if note doesn't exist, None otherwise
    """
    note = keep.get(note_id)
    if note is None:
        return format_error_response(
            "ValueError",
            f"Note {note_id} not found",
            "Use list_all_notes() to see available notes"
        )
    return None


def validate_note_type(note: Any, expected_type: str) -> Optional[Dict[str, Any]]:
    """Validate that a note is of the expected type.
    
    Args:
        note: gkeepapi note object
        expected_type: Expected type ("Note" or "List")
        
    Returns:
        Error response if type doesn't match, None otherwise
    """
    is_list = isinstance(note, gkeepapi.node.List)
    
    if expected_type == "Note" and is_list:
        return format_error_response(
            "TypeError",
            f"Note {note.id} is a List type. Lists do not support text updates. Use add_list_item() instead.",
            None
        )
    elif expected_type == "List" and not is_list:
        return format_error_response(
            "TypeError",
            f"Note {note.id} is a Note type, not a List. Use update_note_text() instead.",
            None
        )
    
    return None


def validate_color(color: str) -> Optional[Dict[str, Any]]:
    """Validate that a color name is valid.
    
    Args:
        color: Color name to validate
        
    Returns:
        Error response if color is invalid, None otherwise
    """
    valid_colors = [
        "White", "Red", "Orange", "Yellow", "Green", "Teal", 
        "Blue", "DarkBlue", "Purple", "Pink", "Brown", "Gray"
    ]
    
    if color not in valid_colors:
        return format_error_response(
            "ValueError",
            f"Invalid color '{color}'",
            f"Valid colors: {', '.join(valid_colors)}"
        )
    
    return None


def safe_execute(operation: str, func, *args, **kwargs) -> Dict[str, Any]:
    """Execute a function with comprehensive error handling.
    
    Args:
        operation: Name of the operation for error reporting
        func: Function to execute
        *args: Positional arguments for func
        **kwargs: Keyword arguments for func
        
    Returns:
        Function result or error response
    """
    try:
        return func(*args, **kwargs)
    except ValueError as e:
        return format_error_response(
            "ValueError",
            str(e),
            "Use list_all_notes() to see available notes"
        )
    except TypeError as e:
        return format_error_response(
            "TypeError",
            str(e),
            None
        )
    except Exception as e:
        logger.exception(f"Unexpected error in {operation}")
        return format_error_response(
            type(e).__name__,
            f"Unexpected error: {str(e)}",
            "Check server logs for details"
        )


logger = logging.getLogger("wlater")


class KeepClient:
    """Wrapper around gkeepapi for read-only Google Keep access."""
    
    def __init__(self, email: str, master_token: str, android_id: str):
        """Initialize and authenticate with Google Keep.
        
        Args:
            email: User's Google email address
            master_token: Google Keep master token
            android_id: 16-character hexadecimal Android ID
            
        Raises:
            RuntimeError: If authentication fails
        """
        self.keep = gkeepapi.Keep()
        
        # Authenticate using resume (no password needed)
        try:
            self.keep.resume(email, master_token, device_id=android_id)
        except Exception as e:
            raise RuntimeError(
                f"Authentication failed: {str(e)}. Token may be expired. "
                "Re-run setup.py to refresh credentials."
            )
        
        # Initial sync to load notes
        self.keep.sync()
        logger.info(f"Authenticated as {email}")
    
    def get_all_notes(self, limit: int = 1000) -> List[Dict[str, Any]]:
        """Retrieve all non-trashed notes and lists.
        
        Args:
            limit: Maximum number of notes to return
            
        Returns:
            List of note dictionaries with basic metadata
        """
        try:
            notes = []
            count = 0
            
            for note in self.keep.all():
                if note.trashed:
                    continue
                    
                notes.append({
                    "note_id": note.id,
                    "title": note.title or "",
                    "note_type": "List" if isinstance(note, gkeepapi.node.List) else "Note",
                    "pinned": note.pinned,
                    "archived": note.archived,
                    "color": note.color.name
                })
                
                count += 1
                if count >= limit:
                    notes.append({"truncated": True, "message": f"Results limited to {limit} notes"})
                    break
            
            return notes
        except Exception as e:
            logger.exception("Unexpected error in get_all_notes")
            raise RuntimeError(f"Failed to retrieve notes: {str(e)}")
    
    def get_note(self, note_id: str) -> Dict[str, Any]:
        """Get detailed content for a specific note.
        
        Args:
            note_id: Google Keep note ID
            
        Returns:
            Dictionary with full note details
            
        Raises:
            ValueError: If note_id doesn't exist
        """
        try:
            note = self.keep.get(note_id)
            
            if note is None:
                raise ValueError(f"Note {note_id} not found")
            
            return {
                "note_id": note.id,
                "title": note.title or "",
                "text": note.text,
                "note_type": "List" if isinstance(note, gkeepapi.node.List) else "Note",
                "color": note.color.name,
                "pinned": note.pinned,
                "archived": note.archived,
                "labels": [{"id": label.id, "name": label.name} for label in note.labels.all()],
                "timestamps": {
                    "created": note.timestamps.created.isoformat(),
                    "updated": note.timestamps.updated.isoformat(),
                    "edited": note.timestamps.edited.isoformat()
                }
            }
        except ValueError:
            # Re-raise ValueError for proper handling by MCP server
            raise
        except Exception as e:
            logger.exception("Unexpected error in get_note")
            raise RuntimeError(f"Failed to get note: {str(e)}")
    
    def get_list_items(self, list_id: str) -> Dict[str, Any]:
        """Get list items with checked status.
        
        Args:
            list_id: Google Keep list ID
            
        Returns:
            Dictionary with all items, checked items, and unchecked items
            
        Raises:
            ValueError: If list_id doesn't exist or is not a List type
        """
        try:
            note = self.keep.get(list_id)
            
            if note is None:
                raise ValueError(f"List {list_id} not found")
            
            if not isinstance(note, gkeepapi.node.List):
                raise ValueError(f"Note {list_id} is not a List type")
            
            all_items = []
            checked_items = []
            unchecked_items = []
            
            for item in note.items:
                item_dict = {
                    "item_id": item.id,
                    "text": item.text,
                    "checked": item.checked,
                    "sort": item.sort
                }
                
                all_items.append(item_dict)
                
                if item.checked:
                    checked_items.append(item_dict)
                else:
                    unchecked_items.append(item_dict)
            
            return {
                "list_id": list_id,
                "title": note.title or "",
                "all_items": all_items,
                "checked_items": checked_items,
                "unchecked_items": unchecked_items
            }
        except ValueError:
            # Re-raise ValueError for proper handling by MCP server
            raise
        except Exception as e:
            logger.exception("Unexpected error in get_list_items")
            raise RuntimeError(f"Failed to get list items: {str(e)}")
    
    def search_notes(
        self,
        query: Optional[str] = None,
        pinned: Optional[bool] = None,
        archived: Optional[bool] = None,
        trashed: Optional[bool] = None,
        colors: Optional[List[str]] = None,
        labels: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Search notes with filters.
        
        Args:
            query: Text to search for (case-insensitive)
            pinned: Filter by pinned status
            archived: Filter by archived status
            trashed: Filter by trashed status
            colors: Filter by color names
            labels: Filter by label names
            limit: Maximum number of results
            
        Returns:
            List of matching note dictionaries
        """
        try:
            # Convert query to case-insensitive regex pattern
            if query:
                # Escape special regex characters and make case-insensitive
                pattern = re.compile(re.escape(query), re.IGNORECASE)
                results = self.keep.find(query=pattern)
            else:
                results = self.keep.all()
            
            notes = []
            count = 0
            
            for note in results:
                # Apply filters
                if pinned is not None and note.pinned != pinned:
                    continue
                if archived is not None and note.archived != archived:
                    continue
                if trashed is not None and note.trashed != trashed:
                    continue
                if colors and note.color.name not in colors:
                    continue
                if labels:
                    note_labels = {label.name for label in note.labels.all()}
                    if not any(label in note_labels for label in labels):
                        continue
                
                notes.append({
                    "note_id": note.id,
                    "title": note.title or "",
                    "note_type": "List" if isinstance(note, gkeepapi.node.List) else "Note",
                    "pinned": note.pinned,
                    "archived": note.archived,
                    "color": note.color.name
                })
                
                count += 1
                if count >= limit:
                    notes.append({"truncated": True, "message": f"Results limited to {limit} notes"})
                    break
            
            return notes
        except Exception as e:
            logger.exception("Unexpected error in search_notes")
            raise RuntimeError(f"Failed to search notes: {str(e)}")
    
    def get_labels(self) -> List[Dict[str, str]]:
        """Get all labels sorted alphabetically.
        
        Returns:
            List of label dictionaries with id and name
        """
        try:
            labels = []
            
            for label in self.keep.labels():
                if not label.deleted:
                    labels.append({
                        "label_id": label.id,
                        "name": label.name
                    })
            
            # Sort alphabetically by name
            labels.sort(key=lambda x: x["name"].lower())
            
            return labels
        except Exception as e:
            logger.exception("Unexpected error in get_labels")
            raise RuntimeError(f"Failed to retrieve labels: {str(e)}")
    
    def find_label(self, name: str) -> Optional[Dict[str, str]]:
        """Find a label by name (case-insensitive).
        
        Args:
            name: Label name to search for
            
        Returns:
            Label dictionary or None if not found
        """
        try:
            label = self.keep.findLabel(name)
            
            if label is None:
                return None
            
            return {
                "label_id": label.id,
                "name": label.name
            }
        except Exception as e:
            logger.exception("Unexpected error in find_label")
            raise RuntimeError(f"Failed to find label: {str(e)}")
    
    # ========================================================================
    # TIER 2: MODIFICATION OPERATIONS (Require explicit sync)
    # ========================================================================
    
    # List Item Operations
    
    def update_list_item_checked(
        self, 
        list_id: str, 
        item_id: str, 
        checked: bool
    ) -> Dict[str, Any]:
        """Update checked status of a list item.
        
        Args:
            list_id: Google Keep list ID
            item_id: List item ID
            checked: New checked status
            
        Returns:
            Preview response with old and new checked status
        """
        try:
            # Get list by ID
            note = self.keep.get(list_id)
            
            if note is None:
                return format_error_response(
                    "ValueError",
                    f"List {list_id} not found",
                    "Use list_all_notes() to see available lists"
                )
            
            # Validate it's a List type
            if not isinstance(note, gkeepapi.node.List):
                return format_error_response(
                    "TypeError",
                    f"Note {list_id} is not a List type",
                    "Use get_note() to check note type"
                )
            
            # Find list item by iterating through list.items
            target_item = None
            for item in note.items:
                if item.id == item_id:
                    target_item = item
                    break
            
            if target_item is None:
                return format_error_response(
                    "ValueError",
                    f"Item {item_id} not found in list {list_id}",
                    "Use get_list_items() to see available items"
                )
            
            # Store old value for preview
            old_checked = target_item.checked
            
            # Set item.checked property
            target_item.checked = checked
            
            # Return preview with old and new checked status
            return format_preview_response(
                "update_list_item_checked",
                {
                    "list_id": list_id,
                    "list_title": note.title or "",
                    "item_id": item_id,
                    "item_text": target_item.text,
                    "old_checked": old_checked,
                    "new_checked": checked
                },
                f"Item checked status updated locally. Call sync_changes() to save to Google Keep."
            )
            
        except Exception as e:
            logger.exception("Unexpected error in update_list_item_checked")
            return format_error_response(
                type(e).__name__,
                f"Unexpected error: {str(e)}",
                "Check server logs for details"
            )
    
    def add_list_item(
        self, 
        list_id: str, 
        text: str, 
        checked: bool = False,
        sort: int = None
    ) -> Dict[str, Any]:
        """Add new item to existing list.
        
        Args:
            list_id: Google Keep list ID
            text: Item text
            checked: Initial checked status (default: False)
            sort: Sort order (optional)
            
        Returns:
            Preview response with new item details
        """
        try:
            # Validate text is not empty
            if not text or not text.strip():
                return format_error_response(
                    "ValueError",
                    "Item text cannot be empty",
                    "Provide a non-empty text value for the list item"
                )
            
            # Get list by ID
            note = self.keep.get(list_id)
            
            if note is None:
                return format_error_response(
                    "ValueError",
                    f"List {list_id} not found",
                    "Use list_all_notes() to see available lists"
                )
            
            # Validate it's a List type
            if not isinstance(note, gkeepapi.node.List):
                return format_error_response(
                    "TypeError",
                    f"Note {list_id} is not a List type",
                    "Use create_note() for text notes"
                )
            
            # Call list.add(text, checked, sort) to add item
            new_item = note.add(text, checked, sort)
            
            # Return preview with new item details
            return format_preview_response(
                "add_list_item",
                {
                    "list_id": list_id,
                    "list_title": note.title or "",
                    "new_item": {
                        "item_id": new_item.id,
                        "text": new_item.text,
                        "checked": new_item.checked,
                        "sort": new_item.sort
                    }
                },
                f"Item added to list locally. Call sync_changes() to save to Google Keep."
            )
            
        except Exception as e:
            logger.exception("Unexpected error in add_list_item")
            return format_error_response(
                type(e).__name__,
                f"Unexpected error: {str(e)}",
                "Check server logs for details"
            )
    
    # Note Creation
    
    def create_note(
        self, 
        title: str = "", 
        text: str = ""
    ) -> Dict[str, Any]:
        """Create new text note.
        
        Args:
            title: Note title (default: empty)
            text: Note text content (default: empty)
            
        Returns:
            Preview response with note ID, title, and text
        """
        try:
            # Call keep.createNote(title, text)
            new_note = self.keep.createNote(title, text)
            
            # Return preview with note ID, title, and text
            return format_preview_response(
                "create_note",
                {
                    "note_id": new_note.id,
                    "title": new_note.title or "",
                    "text": new_note.text or "",
                    "note_type": "Note",
                    "color": new_note.color.name
                },
                f"Note created locally. Call sync_changes() to save to Google Keep."
            )
            
        except Exception as e:
            logger.exception("Unexpected error in create_note")
            return format_error_response(
                type(e).__name__,
                f"Unexpected error: {str(e)}",
                "Check server logs for details"
            )
    
    def create_list(
        self, 
        title: str = "", 
        items: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create new list with items.
        
        Args:
            title: List title (default: empty)
            items: List of items with format [{"text": "...", "checked": False}, ...]
            
        Returns:
            Preview response with list ID, title, and items
        """
        try:
            # Format items as list of tuples: [(text, checked), ...]
            formatted_items = []
            if items:
                for item in items:
                    text = item.get("text", "")
                    checked = item.get("checked", False)
                    formatted_items.append((text, checked))
            
            # Call keep.createList(title, items)
            new_list = self.keep.createList(title, formatted_items)
            
            # Build preview items
            preview_items = []
            for item in new_list.items:
                preview_items.append({
                    "item_id": item.id,
                    "text": item.text,
                    "checked": item.checked,
                    "sort": item.sort
                })
            
            # Return preview with list ID, title, and items
            return format_preview_response(
                "create_list",
                {
                    "list_id": new_list.id,
                    "title": new_list.title or "",
                    "note_type": "List",
                    "color": new_list.color.name,
                    "items": preview_items,
                    "item_count": len(preview_items)
                },
                f"List created locally with {len(preview_items)} items. Call sync_changes() to save to Google Keep."
            )
            
        except Exception as e:
            logger.exception("Unexpected error in create_list")
            return format_error_response(
                type(e).__name__,
                f"Unexpected error: {str(e)}",
                "Check server logs for details"
            )
    
    # Note Updates
    
    def update_note_title(
        self, 
        note_id: str, 
        title: str
    ) -> Dict[str, Any]:
        """Update note title.
        
        Args:
            note_id: Google Keep note ID
            title: New title
            
        Returns:
            Preview response with old and new title
        """
        try:
            # Get note by ID using keep.get()
            note = self.keep.get(note_id)
            
            if note is None:
                return format_error_response(
                    "ValueError",
                    f"Note {note_id} not found",
                    "Use list_all_notes() to see available notes"
                )
            
            # Store old title value
            old_title = note.title or ""
            
            # Set note.title property
            note.title = title
            
            # Return preview with old and new title
            return format_preview_response(
                "update_note_title",
                {
                    "note_id": note_id,
                    "note_type": "List" if isinstance(note, gkeepapi.node.List) else "Note",
                    "old_title": old_title,
                    "new_title": title
                },
                f"Note title updated locally. Call sync_changes() to save to Google Keep."
            )
            
        except Exception as e:
            logger.exception("Unexpected error in update_note_title")
            return format_error_response(
                type(e).__name__,
                f"Unexpected error: {str(e)}",
                "Check server logs for details"
            )
    
    def update_note_text(
        self, 
        note_id: str, 
        text: str
    ) -> Dict[str, Any]:
        """Update note text content.
        
        Args:
            note_id: Google Keep note ID
            text: New text content
            
        Returns:
            Preview response with old and new text
        """
        try:
            # Get note by ID using keep.get()
            note = self.keep.get(note_id)
            
            if note is None:
                return format_error_response(
                    "ValueError",
                    f"Note {note_id} not found",
                    "Use list_all_notes() to see available notes"
                )
            
            # Check if note is List type (raise error if true)
            if isinstance(note, gkeepapi.node.List):
                return format_error_response(
                    "TypeError",
                    f"Note {note_id} is a List type. Lists do not support text updates. Use add_list_item() instead.",
                    None
                )
            
            # Store old text value
            old_text = note.text or ""
            
            # Set note.text property
            note.text = text
            
            # Return preview with old and new text
            return format_preview_response(
                "update_note_text",
                {
                    "note_id": note_id,
                    "note_title": note.title or "",
                    "old_text": old_text,
                    "new_text": text
                },
                f"Note text updated locally. Call sync_changes() to save to Google Keep."
            )
            
        except Exception as e:
            logger.exception("Unexpected error in update_note_text")
            return format_error_response(
                type(e).__name__,
                f"Unexpected error: {str(e)}",
                "Check server logs for details"
            )
    
    # Note Properties
    
    def update_note_color(
        self, 
        note_id: str, 
        color: str
    ) -> Dict[str, Any]:
        """Update note color.
        
        Args:
            note_id: Google Keep note ID
            color: Color name (White, Red, Orange, Yellow, Green, Teal, 
                   Blue, DarkBlue, Purple, Pink, Brown, Gray)
            
        Returns:
            Preview response with new color
        """
        try:
            # Validate color name
            valid_colors = [
                "White", "Red", "Orange", "Yellow", "Green", "Teal", 
                "Blue", "DarkBlue", "Purple", "Pink", "Brown", "Gray"
            ]
            
            if color not in valid_colors:
                return format_error_response(
                    "ValueError",
                    f"Invalid color '{color}'",
                    f"Valid colors: {', '.join(valid_colors)}"
                )
            
            # Get note by ID using keep.get()
            note = self.keep.get(note_id)
            
            if note is None:
                return format_error_response(
                    "ValueError",
                    f"Note {note_id} not found",
                    "Use list_all_notes() to see available notes"
                )
            
            # Store old color for preview
            old_color = note.color.name
            
            # Map color string to gkeepapi.node.ColorValue enum
            color_value = getattr(gkeepapi.node.ColorValue, color)
            
            # Set note.color property
            note.color = color_value
            
            # Return preview with new color
            return format_preview_response(
                "update_note_color",
                {
                    "note_id": note_id,
                    "note_title": note.title or "",
                    "note_type": "List" if isinstance(note, gkeepapi.node.List) else "Note",
                    "old_color": old_color,
                    "new_color": color
                },
                f"Note color updated locally. Call sync_changes() to save to Google Keep."
            )
            
        except Exception as e:
            logger.exception("Unexpected error in update_note_color")
            return format_error_response(
                type(e).__name__,
                f"Unexpected error: {str(e)}",
                "Check server logs for details"
            )
    
    def update_note_pinned(
        self, 
        note_id: str, 
        pinned: bool
    ) -> Dict[str, Any]:
        """Pin or unpin note.
        
        Args:
            note_id: Google Keep note ID
            pinned: New pinned status
            
        Returns:
            Preview response with new pinned status
        """
        try:
            # Get note by ID using keep.get()
            note = self.keep.get(note_id)
            
            if note is None:
                return format_error_response(
                    "ValueError",
                    f"Note {note_id} not found",
                    "Use list_all_notes() to see available notes"
                )
            
            # Store old pinned status for preview
            old_pinned = note.pinned
            
            # Set note.pinned property
            note.pinned = pinned
            
            # Return preview with new pinned status
            return format_preview_response(
                "update_note_pinned",
                {
                    "note_id": note_id,
                    "note_title": note.title or "",
                    "note_type": "List" if isinstance(note, gkeepapi.node.List) else "Note",
                    "old_pinned": old_pinned,
                    "new_pinned": pinned
                },
                f"Note pinned status updated locally. Call sync_changes() to save to Google Keep."
            )
            
        except Exception as e:
            logger.exception("Unexpected error in update_note_pinned")
            return format_error_response(
                type(e).__name__,
                f"Unexpected error: {str(e)}",
                "Check server logs for details"
            )
    
    def update_note_archived(
        self, 
        note_id: str, 
        archived: bool
    ) -> Dict[str, Any]:
        """Archive or unarchive note.
        
        Args:
            note_id: Google Keep note ID
            archived: New archived status
            
        Returns:
            Preview response with new archived status
        """
        try:
            # Get note by ID using keep.get()
            note = self.keep.get(note_id)
            
            if note is None:
                return format_error_response(
                    "ValueError",
                    f"Note {note_id} not found",
                    "Use list_all_notes() to see available notes"
                )
            
            # Store old archived status for preview
            old_archived = note.archived
            
            # Set note.archived property
            note.archived = archived
            
            # Return preview with new archived status
            return format_preview_response(
                "update_note_archived",
                {
                    "note_id": note_id,
                    "note_title": note.title or "",
                    "note_type": "List" if isinstance(note, gkeepapi.node.List) else "Note",
                    "old_archived": old_archived,
                    "new_archived": archived
                },
                f"Note archived status updated locally. Call sync_changes() to save to Google Keep."
            )
            
        except Exception as e:
            logger.exception("Unexpected error in update_note_archived")
            return format_error_response(
                type(e).__name__,
                f"Unexpected error: {str(e)}",
                "Check server logs for details"
            )
    
    # Label Operations
    
    def create_label(
        self, 
        name: str
    ) -> Dict[str, Any]:
        """Create new label.
        
        Args:
            name: Label name
            
        Returns:
            Preview response with label ID and name
        """
        try:
            # Validate label name is not empty
            if not name or not name.strip():
                return format_error_response(
                    "ValueError",
                    "Label name cannot be empty",
                    "Provide a non-empty name for the label"
                )
            
            # Check if label already exists
            existing_label = self.keep.findLabel(name)
            if existing_label is not None:
                return format_error_response(
                    "ValueError",
                    f"Label '{name}' already exists",
                    "Use a different name or use add_label_to_note() to add the existing label to a note"
                )
            
            # Call keep.createLabel(name)
            new_label = self.keep.createLabel(name)
            
            # Return preview with label ID and name
            return format_preview_response(
                "create_label",
                {
                    "label_id": new_label.id,
                    "name": new_label.name
                },
                f"Label '{name}' created locally. Call sync_changes() to save to Google Keep."
            )
            
        except Exception as e:
            logger.exception("Unexpected error in create_label")
            return format_error_response(
                type(e).__name__,
                f"Unexpected error: {str(e)}",
                "Check server logs for details"
            )
    
    def add_label_to_note(
        self, 
        note_id: str, 
        label_name: str
    ) -> Dict[str, Any]:
        """Add label to note.
        
        Args:
            note_id: Google Keep note ID
            label_name: Label name to add
            
        Returns:
            Preview response with note title and updated labels
        """
        try:
            # Get note by ID using keep.get()
            note = self.keep.get(note_id)
            
            if note is None:
                return format_error_response(
                    "ValueError",
                    f"Note {note_id} not found",
                    "Use list_all_notes() to see available notes"
                )
            
            # Find label using keep.findLabel(label_name)
            label = self.keep.findLabel(label_name)
            
            if label is None:
                return format_error_response(
                    "ValueError",
                    f"Label '{label_name}' not found",
                    "Use list_labels() to see available labels or create_label() to create a new one"
                )
            
            # Check if label is already on the note
            existing_labels = {lbl.name for lbl in note.labels.all()}
            if label_name in existing_labels:
                return format_error_response(
                    "ValueError",
                    f"Label '{label_name}' is already on note {note_id}",
                    "Use remove_label_from_note() to remove it first if you want to re-add it"
                )
            
            # Call note.labels.add(label)
            note.labels.add(label)
            
            # Build updated labels list for preview
            updated_labels = [{"id": lbl.id, "name": lbl.name} for lbl in note.labels.all()]
            
            # Return preview with note title and updated labels
            return format_preview_response(
                "add_label_to_note",
                {
                    "note_id": note_id,
                    "note_title": note.title or "",
                    "note_type": "List" if isinstance(note, gkeepapi.node.List) else "Note",
                    "label_added": label_name,
                    "updated_labels": updated_labels
                },
                f"Label '{label_name}' added to note locally. Call sync_changes() to save to Google Keep."
            )
            
        except Exception as e:
            logger.exception("Unexpected error in add_label_to_note")
            return format_error_response(
                type(e).__name__,
                f"Unexpected error: {str(e)}",
                "Check server logs for details"
            )
    
    def remove_label_from_note(
        self, 
        note_id: str, 
        label_name: str
    ) -> Dict[str, Any]:
        """Remove label from note.
        
        Args:
            note_id: Google Keep note ID
            label_name: Label name to remove
            
        Returns:
            Preview response with note title and updated labels
        """
        try:
            # Get note by ID using keep.get()
            note = self.keep.get(note_id)
            
            if note is None:
                return format_error_response(
                    "ValueError",
                    f"Note {note_id} not found",
                    "Use list_all_notes() to see available notes"
                )
            
            # Find label using keep.findLabel(label_name)
            label = self.keep.findLabel(label_name)
            
            if label is None:
                return format_error_response(
                    "ValueError",
                    f"Label '{label_name}' not found",
                    "Use list_labels() to see available labels"
                )
            
            # Check if label is on the note
            existing_labels = {lbl.name for lbl in note.labels.all()}
            if label_name not in existing_labels:
                return format_error_response(
                    "ValueError",
                    f"Label '{label_name}' is not on note {note_id}",
                    "Use add_label_to_note() to add it first or list_labels() to see available labels"
                )
            
            # Call note.labels.remove(label)
            note.labels.remove(label)
            
            # Build updated labels list for preview
            updated_labels = [{"id": lbl.id, "name": lbl.name} for lbl in note.labels.all()]
            
            # Return preview with note title and updated labels
            return format_preview_response(
                "remove_label_from_note",
                {
                    "note_id": note_id,
                    "note_title": note.title or "",
                    "note_type": "List" if isinstance(note, gkeepapi.node.List) else "Note",
                    "label_removed": label_name,
                    "updated_labels": updated_labels
                },
                f"Label '{label_name}' removed from note locally. Call sync_changes() to save to Google Keep."
            )
            
        except Exception as e:
            logger.exception("Unexpected error in remove_label_from_note")
            return format_error_response(
                type(e).__name__,
                f"Unexpected error: {str(e)}",
                "Check server logs for details"
            )
    
    # Sync Control
    
    def sync_changes(self) -> Dict[str, Any]:
        """Sync all pending changes to Google Keep.
        
        Returns:
            Confirmation with sync timestamp and number of changes
        """
        try:
            # Track number of changes before sync (if possible)
            # Note: gkeepapi doesn't provide a direct way to count pending changes
            # We'll sync and report success
            
            # Call keep.sync() to push all pending changes
            self.keep.sync()
            
            # Generate timestamp
            timestamp = datetime.utcnow().isoformat() + "Z"
            
            # Return confirmation with sync timestamp
            return {
                "success": True,
                "operation": "sync",
                "timestamp": timestamp,
                "message": "Successfully synced all pending changes to Google Keep"
            }
            
        except Exception as e:
            logger.exception("Unexpected error in sync_changes")
            return format_error_response(
                type(e).__name__,
                f"Sync failed: {str(e)}",
                "Check network connection and credentials"
            )
    
    def get_pending_changes(self) -> Dict[str, Any]:
        """Get preview of all pending changes.
        
        Returns:
            Structured preview of all pending changes
        """
        try:
            changes = []
            
            # Iterate through all notes to find dirty/modified notes
            for note in self.keep.all():
                # Check if note is dirty (has pending changes)
                if note.dirty:
                    # Determine change type based on note state
                    change_type = "modified"
                    details = ""
                    
                    # Check if it's a new note (no timestamps yet or very recent)
                    if hasattr(note, 'timestamps') and note.timestamps.created == note.timestamps.updated:
                        change_type = "created"
                        if isinstance(note, gkeepapi.node.List):
                            details = f"New list with {len(note.items)} items"
                        else:
                            details = "New note created"
                    else:
                        # For modified notes, provide generic details
                        if isinstance(note, gkeepapi.node.List):
                            details = "List modified"
                        else:
                            details = "Note modified"
                    
                    # Build list of changes with note IDs and change types
                    changes.append({
                        "note_id": note.id,
                        "note_title": note.title or "(Untitled)",
                        "note_type": "List" if isinstance(note, gkeepapi.node.List) else "Note",
                        "change_type": change_type,
                        "details": details
                    })
            
            # Return structured preview of all pending changes
            has_changes = len(changes) > 0
            
            return {
                "success": True,
                "has_changes": has_changes,
                "change_count": len(changes),
                "changes": changes,
                "message": f"Found {len(changes)} pending change(s)" if has_changes else "No pending changes"
            }
            
        except Exception as e:
            logger.exception("Unexpected error in get_pending_changes")
            return format_error_response(
                type(e).__name__,
                f"Failed to get pending changes: {str(e)}",
                "Check server logs for details"
            )
    
    def refresh_from_server(self) -> Dict[str, Any]:
        """Refresh local cache from Google Keep server.
        
        Returns:
            Confirmation message
        """
        try:
            # Call keep.sync() to fetch latest data and push pending changes
            # Note: keep.sync() both pushes local changes AND pulls server changes
            self.keep.sync()
            
            # Generate timestamp
            timestamp = datetime.utcnow().isoformat() + "Z"
            
            # Return confirmation message
            return {
                "success": True,
                "operation": "refresh",
                "timestamp": timestamp,
                "message": "Successfully refreshed local cache from Google Keep server"
            }
            
        except Exception as e:
            logger.exception("Unexpected error in refresh_from_server")
            return format_error_response(
                type(e).__name__,
                f"Refresh failed: {str(e)}",
                "Check network connection and credentials"
            )
    
    # Media Operations (Read-Only)
    
    def get_note_media(
        self, 
        note_id: str
    ) -> Dict[str, Any]:
        """Get all media attachments from a note.
        
        Args:
            note_id: Google Keep note ID
            
        Returns:
            Structured media information with metadata
        """
        try:
            # Get note by ID using keep.get()
            note = self.keep.get(note_id)
            
            if note is None:
                return format_error_response(
                    "ValueError",
                    f"Note {note_id} not found",
                    "Use list_all_notes() to see available notes"
                )
            
            # Access note.images, note.drawings, note.audio
            images = []
            for img in note.images:
                # Extract metadata (width, height, byte_size, extracted_text)
                img_data = {
                    "blob_id": img.id,
                    "type": "image"
                }
                
                # Add optional metadata if available
                if hasattr(img, 'width') and img.width:
                    img_data["width"] = img.width
                if hasattr(img, 'height') and img.height:
                    img_data["height"] = img.height
                if hasattr(img, 'byte_size') and img.byte_size:
                    img_data["byte_size"] = img.byte_size
                if hasattr(img, 'extracted_text') and img.extracted_text:
                    img_data["extracted_text"] = img.extracted_text
                
                images.append(img_data)
            
            drawings = []
            for draw in note.drawings:
                # Extract metadata (extracted_text)
                draw_data = {
                    "blob_id": draw.id,
                    "type": "drawing"
                }
                
                if hasattr(draw, 'extracted_text') and draw.extracted_text:
                    draw_data["extracted_text"] = draw.extracted_text
                
                drawings.append(draw_data)
            
            audio = []
            for aud in note.audio:
                # Extract metadata (length)
                aud_data = {
                    "blob_id": aud.id,
                    "type": "audio"
                }
                
                if hasattr(aud, 'length') and aud.length:
                    aud_data["length"] = aud.length
                
                audio.append(aud_data)
            
            # Return structured media information
            total_media = len(images) + len(drawings) + len(audio)
            
            return {
                "success": True,
                "note_id": note_id,
                "note_title": note.title or "",
                "media": {
                    "images": images,
                    "drawings": drawings,
                    "audio": audio
                },
                "total_media": total_media
            }
            
        except Exception as e:
            logger.exception("Unexpected error in get_note_media")
            return format_error_response(
                type(e).__name__,
                f"Failed to get media: {str(e)}",
                "Check server logs for details"
            )
    
    def get_media_link(
        self, 
        note_id: str,
        blob_id: str
    ) -> Dict[str, Any]:
        """Get download URL for a media blob.
        
        Args:
            note_id: Google Keep note ID
            blob_id: Media blob ID
            
        Returns:
            URL with media metadata
        """
        try:
            # Get note by ID using keep.get()
            note = self.keep.get(note_id)
            
            if note is None:
                return format_error_response(
                    "ValueError",
                    f"Note {note_id} not found",
                    "Use list_all_notes() to see available notes"
                )
            
            # Find blob by ID in note.images, note.drawings, or note.audio
            blob = None
            media_type = None
            
            # Search in images
            for img in note.images:
                if img.id == blob_id:
                    blob = img
                    media_type = "image"
                    break
            
            # Search in drawings if not found
            if blob is None:
                for draw in note.drawings:
                    if draw.id == blob_id:
                        blob = draw
                        media_type = "drawing"
                        break
            
            # Search in audio if not found
            if blob is None:
                for aud in note.audio:
                    if aud.id == blob_id:
                        blob = aud
                        media_type = "audio"
                        break
            
            # If blob not found, return error
            if blob is None:
                return format_error_response(
                    "ValueError",
                    f"Media blob {blob_id} not found in note {note_id}",
                    "Use get_note_media() to see available media blobs"
                )
            
            # Call keep.getMediaLink(blob) to get download URL
            download_url = self.keep.getMediaLink(blob)
            
            # Return URL with media metadata
            return {
                "success": True,
                "note_id": note_id,
                "blob_id": blob_id,
                "media_type": media_type,
                "download_url": download_url,
                "expires": "URL is temporary and may expire"
            }
            
        except Exception as e:
            logger.exception("Unexpected error in get_media_link")
            return format_error_response(
                type(e).__name__,
                f"Failed to get media link: {str(e)}",
                "Check server logs for details"
            )

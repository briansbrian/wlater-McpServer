"""Google Keep client wrapper for read-only operations."""

import logging
from typing import List, Dict, Optional, Any

import gkeepapi


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
    
    def get_note(self, note_id: str) -> Dict[str, Any]:
        """Get detailed content for a specific note.
        
        Args:
            note_id: Google Keep note ID
            
        Returns:
            Dictionary with full note details
            
        Raises:
            ValueError: If note_id doesn't exist
        """
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
    
    def get_list_items(self, list_id: str) -> Dict[str, Any]:
        """Get list items with checked status.
        
        Args:
            list_id: Google Keep list ID
            
        Returns:
            Dictionary with all items, checked items, and unchecked items
            
        Raises:
            ValueError: If list_id doesn't exist or is not a List type
        """
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
            query: Text to search for
            pinned: Filter by pinned status
            archived: Filter by archived status
            trashed: Filter by trashed status
            colors: Filter by color names
            labels: Filter by label names
            limit: Maximum number of results
            
        Returns:
            List of matching note dictionaries
        """
        # Start with all notes or search results
        if query:
            results = self.keep.find(query=query)
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
    
    def get_labels(self) -> List[Dict[str, str]]:
        """Get all labels sorted alphabetically.
        
        Returns:
            List of label dictionaries with id and name
        """
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
    
    def find_label(self, name: str) -> Optional[Dict[str, str]]:
        """Find a label by name (case-insensitive).
        
        Args:
            name: Label name to search for
            
        Returns:
            Label dictionary or None if not found
        """
        label = self.keep.findLabel(name)
        
        if label is None:
            return None
        
        return {
            "label_id": label.id,
            "name": label.name
        }

---
inclusion: always
---

# Tier 2 Modifications - Safety-First Write Operations

## Core Principles

**Never Auto-Sync**: Modifications update local state only. The `keep.sync()` method must NEVER be called automatically - only through explicit `sync_changes()` tool invocation.

**Preview Before Commit**: Every modification returns a preview showing old/new values. Users review changes before syncing.

**Explicit User Control**: All write operations require manual sync via `sync_changes()` tool. This is the ONLY way changes reach Google Keep servers.

## Architecture Pattern

```
Modification Tool → Update Local State → Return Preview (NOT synced)
                                              ↓
                                    User Reviews Preview
                                              ↓
                                    sync_changes() Tool → Push to Server
```

## Response Format Standards

### Modification Response
```python
{
    "success": True,
    "operation": "update_list_item_checked",
    "preview": {
        "note_id": "abc123",
        "note_title": "Shopping List",
        "old_value": False,
        "new_value": True
    },
    "synced": False,  # Always False for modifications
    "message": "Updated locally. Call sync_changes() to save."
}
```

### Sync Response
```python
{
    "success": True,
    "operation": "sync",
    "changes_synced": 3,
    "timestamp": "2025-11-14T12:34:56Z",
    "message": "Successfully synced 3 changes to Google Keep"
}
```

## FastMCP Tool Pattern

Use `@mcp.tool` decorator without parentheses (FastMCP 2.7+ syntax):

```python
@mcp.tool
def update_note_title(note_id: str, title: str) -> dict:
    """Update note title (requires sync).
    
    Changes are local only. Call sync_changes() to save to Google Keep.
    """
    keep_client = get_keep_client()
    return keep_client.update_note_title(note_id, title)
```

## Error Handling

Return structured error responses, never raise exceptions to user:

```python
try:
    note = self.keep.get(note_id)
    if note is None:
        return {
            "success": False,
            "error": "ValueError",
            "message": f"Note {note_id} not found",
            "suggestion": "Use list_all_notes() to see available notes"
        }
    # ... perform operation
except Exception as e:
    return {
        "success": False,
        "error": type(e).__name__,
        "message": str(e),
        "suggestion": "Check server logs for details"
    }
```

## Tier 2 Operations (Priority Order)

1. **List Item Operations** (highest demand)
   - `update_list_item_checked()` - Check/uncheck todos
   - `add_list_item()` - Add items to existing lists

2. **Note Creation**
   - `create_note()` - Create text notes
   - `create_list()` - Create lists with items

3. **Note Updates**
   - `update_note_title()`, `update_note_text()`
   - `update_note_color()`, `update_note_pinned()`, `update_note_archived()`

4. **Label Management**
   - `create_label()`, `add_label_to_note()`, `remove_label_from_note()`

5. **Sync Control** (critical)
   - `sync_changes()` - Push all pending changes
   - `get_pending_changes()` - Preview what will sync
   - `refresh_notes()` - Pull latest from server

## Type Validation

Check note types before operations:

```python
if isinstance(note, gkeepapi.node.List):
    return {
        "success": False,
        "error": "TypeError",
        "message": "Note is a List. Use add_list_item() instead.",
        "suggestion": None
    }
```

## Never Expose (Tier 3)

- `note.delete()`, `note.trash()` - Destructive operations
- `deleteLabel()` - Account-wide deletion
- `login()` - Security risk

## Testing Requirements

- Mock gkeepapi in unit tests
- Verify modifications don't call `keep.sync()`
- Test error responses for invalid IDs
- Test type validation (Note vs List)
- Verify preview format matches standard

## Documentation Requirements

- Tool descriptions must state "(requires sync)"
- Include example showing modify → preview → sync workflow
- Warn about pending changes being lost on server restart
- Document color names: White, Red, Orange, Yellow, Green, Teal, Blue, DarkBlue, Purple, Pink, Brown, Gray
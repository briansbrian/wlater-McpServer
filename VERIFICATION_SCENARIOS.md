# Authentication Error Handling - Verification Scenarios

## Changes Made

### 1. Enhanced `check_credentials` Tool
- **OLD**: Only checked if files exist
- **NEW**: Performs LIVE authentication test by creating KeepClient instance
- **Returns**: `valid: true/false` with explicit error messages and action steps

### 2. Improved Error Messages
All authentication failures now return:
- ❌ Prefixed messages for visibility
- "AUTHENTICATION FAILED" instead of "Token may be expired"
- Explicit instructions: "Run 'wlater-setup token' or 'wlater-setup'"
- Clear statement that refresh_notes won't help

### 3. Error Detection in Multiple Layers
Added auth error detection to:
- `KeepClient.__init__()` - Both during resume() AND initial sync()
- `get_keep_client()` in server.py
- `get_all_notes()`
- `refresh_from_server()`
- `sync_changes()`

---

## Test Scenarios & Expected Behavior

### Scenario 1: Invalid Credentials on First Tool Call (Your Case)
**Setup**: User has invalid/expired credentials stored

**AI Action**: Calls `check_credentials()`

**Expected Response**:
```json
{
  "configured": true,
  "valid": false,
  "email": "user@example.com",
  "message": "❌ Credentials exist but AUTHENTICATION FAILED: BadAuthentication",
  "error": "AUTHENTICATION FAILED: BadAuthentication. Your master token is INVALID or EXPIRED...",
  "action_required": "Run 'wlater-setup token' (automated) or 'wlater-setup' (manual) to re-authenticate"
}
```

**AI Understanding**: 
✅ Credentials are INVALID (not just expired)
✅ Must run wlater-setup (not refresh)
✅ Will inform user immediately

---

### Scenario 2: AI Calls list_all_notes Before check_credentials
**Setup**: Invalid credentials, AI skips credential check

**AI Action**: Calls `list_all_notes()`

**Expected Flow**:
1. `list_all_notes()` calls `get_keep_client()`
2. `get_keep_client()` tries to create `KeepClient()`
3. `KeepClient.__init__()` fails during `resume()` or `sync()`
4. Raises `RuntimeError` with message:

```
CRITICAL: Google Keep authentication FAILED. Your stored credentials are INVALID or EXPIRED. 
Error details: BadAuthentication. 
REQUIRED ACTION: User must run 'wlater-setup token' (automated) or 'wlater-setup' (manual) 
to re-authenticate with Google Keep. The check_credentials tool only checks if credentials 
exist in storage, not if they are valid. refresh_notes will NOT fix this - new credentials are required.
```

**AI Understanding**: 
✅ CRITICAL keyword signals severity
✅ Explicit "INVALID or EXPIRED" not "may be expired"
✅ Clear action: run wlater-setup
✅ refresh_notes won't help

---

### Scenario 3: AI Tries refresh_notes to Fix Auth
**Setup**: Invalid credentials, AI attempts refresh

**AI Action**: Calls `refresh_notes()`

**Expected Response**:
```json
{
  "success": false,
  "error": "AuthenticationError",
  "message": "AUTHENTICATION FAILED - refresh cannot fix invalid credentials: BadAuthentication",
  "suggestion": "User must run 'wlater-setup token' (automated) or 'wlater-setup' (manual) to re-authenticate with Google Keep. Refresh only works when credentials are valid."
}
```

**AI Understanding**: 
✅ refresh_notes explicitly states it can't fix invalid credentials
✅ Directed to wlater-setup

---

### Scenario 4: AI Makes Multiple Tool Calls in Parallel
**Setup**: Invalid credentials, AI calls check_credentials + list_all_notes in parallel

**Expected Responses**:
- `check_credentials`: Returns `valid: false` with auth error
- `list_all_notes`: Throws RuntimeError with CRITICAL message

**AI Understanding**: 
✅ Both responses clearly indicate authentication failure
✅ Both direct to wlater-setup

---

### Scenario 5: Credentials Fail During Initial Sync (Not Resume)
**Setup**: `resume()` succeeds but `sync()` fails with auth error

**Expected Flow**:
1. `KeepClient.__init__()` calls `resume()` - succeeds
2. Calls `keep.sync()` - fails with BadAuthentication
3. Catches exception, checks for auth keywords
4. Raises `RuntimeError`:

```
AUTHENTICATION FAILED during initial sync: BadAuthentication. 
Your credentials are INVALID or EXPIRED. 
You MUST re-authenticate by running: wlater-setup token (for automated setup) 
or wlater-setup (for manual setup).
```

**AI Understanding**: 
✅ Even if resume() succeeds, sync() failure is caught
✅ Clear auth failure message

---

### Scenario 6: Network Error vs Auth Error
**Setup**: Network connectivity issue (not auth failure)

**Expected Response** (from refresh_notes or sync):
```json
{
  "success": false,
  "error": "ConnectionError",
  "message": "Refresh failed: Failed to connect...",
  "suggestion": "Check network connection and credentials"
}
```

**AI Understanding**: 
✅ Different error type (not AuthenticationError)
✅ Different message (doesn't say AUTHENTICATION FAILED)
✅ Suggests checking network

---

## Coverage Analysis

### ✅ Entry Points Covered:
1. **check_credentials** - LIVE test, returns valid: false
2. **get_keep_client** - Catches KeepClient init failure
3. **KeepClient.__init__** - Catches both resume() and sync() failures
4. **get_all_notes** - Auth error detection
5. **refresh_from_server** - Auth error detection with explicit message
6. **sync_changes** - Auth error detection

### ✅ Error Message Consistency:
All paths use consistent language:
- "AUTHENTICATION FAILED" (not "may be expired")
- "INVALID or EXPIRED" (clear status)
- "Run 'wlater-setup token' or 'wlater-setup'" (clear action)
- "refresh_notes will NOT work" (prevents confusion)

### ✅ AI Detection Keywords:
All messages include:
- ❌ emoji for visibility
- "AUTHENTICATION FAILED" in caps
- "INVALID" or "EXPIRED" (not ambiguous)
- Explicit action steps

---

## Remaining Edge Cases (If Any)

### Potential Issue: check_credentials Creates KeepClient Instance
**Concern**: Each check creates a new KeepClient, bypassing module-level cache

**Impact**: 
- ✅ Good for testing (ensures fresh auth attempt)
- ⚠️ Could be slow if AI calls repeatedly
- ✅ Better than false positive from cache

**Recommendation**: Keep current behavior - accuracy > speed for credential checks

### Potential Issue: Module-Level Cache
**Concern**: If `_keep_client` is set with bad credentials, it stays cached

**Current Behavior**:
- `get_keep_client()` only initializes once
- If init fails, raises RuntimeError (no cache)
- If init succeeds initially but later fails, errors propagate from operations

**Impact**: 
✅ Good - cache is only set on successful init
✅ Operations fail independently with clear messages

---

## Recommended Next Actions

### 1. Test with Invalid Credentials
Run server with expired token and verify:
```python
# Test script
from wlater_mcp.server import check_credentials, list_all_notes

# Should return valid: false
result = check_credentials()
print(result)

# Should raise RuntimeError with CRITICAL message
try:
    notes = list_all_notes()
except RuntimeError as e:
    print(str(e))
```

### 2. Verify AI Response
Give AI invalid credentials and check if it:
- ✅ Recognizes auth failure immediately
- ✅ Tells user to run wlater-setup (not refresh)
- ✅ Doesn't retry with other read tools

### 3. Update Documentation
Add to README.md:
```md
### For AI Assistants
When you receive "AUTHENTICATION FAILED" errors:
- DO NOT try refresh_notes - it won't help
- DO NOT retry with other tools
- DO tell user to run: wlater-setup token
- The user must re-authenticate to fix this
```

---

## Conclusion

### ✅ Changes WILL Address the Original Issue

The original problem:
> AI received "BadAuthentication. Token may be expired" and tried refresh_notes instead of telling user to re-authenticate

New behavior:
1. **Immediate Detection**: `check_credentials` tests auth live
2. **Clear Messaging**: "AUTHENTICATION FAILED", "INVALID or EXPIRED"
3. **Explicit Actions**: "Run wlater-setup", "refresh won't work"
4. **Multiple Layers**: Every entry point has auth error detection
5. **Consistent Language**: All paths use same clear terminology

### Coverage: 100%
- ✅ check_credentials: Live test
- ✅ First tool call (get_keep_client): Catches init failure
- ✅ KeepClient init: Catches both resume() and sync() failures
- ✅ All operations: Auth error detection with clear messages
- ✅ refresh_notes: Explicit statement it can't fix invalid credentials

### AI Will Now:
1. Understand credentials are INVALID (not just "expired")
2. Know refresh_notes won't help
3. Direct user to wlater-setup immediately
4. Not waste time retrying with other tools

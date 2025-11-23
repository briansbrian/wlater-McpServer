# Wlater-MCP + Kiro Agent Hooks: Workflow Automation Guide

## Overview

This guide explores powerful workflow automations by combining **wlater-mcp** (Google Keep integration) with **Kiro Agent Hooks** (event-driven automation). These integrations transform Google Keep into a dynamic project management and knowledge capture system.

## What Are Agent Hooks?

Agent hooks are automated Kiro executions triggered by IDE events or manual buttons. They enable:
- Automatic task logging on file saves
- Context-aware note updates
- Event-driven documentation
- Seamless knowledge capture

## Core Integration Patterns

### 1. Automatic Task Logging

**Use Case:** Log completed work without manual intervention

#### Hook: On File Save → Log Task
```yaml
Trigger: File Save
Condition: Files matching pattern (*.py, *.ts, *.md)
Action: Log task to today's Google Keep note
```

**Implementation:**
- Detect what changed (git diff)
- Generate task description from commit-like message
- Append to "Project Name - [YYYY-MM-DD]" note
- Add timestamp and file references

**Example Output:**
```
✅ [14:32] Implemented JWT authentication
   📁 Modified: src/auth/jwt_handler.py, tests/test_auth.py
   🔧 Added token generation and validation functions
```

---

### 2. Feature Completion Tracking

**Use Case:** Track feature progress across multiple files

#### Hook: On Test Pass → Update Feature Status
```yaml
Trigger: Test execution completes successfully
Condition: Test file matches feature pattern
Action: Update feature checklist in Google Keep
```

**Implementation:**
- Parse test results
- Identify completed feature components
- Update feature note with checkboxes
- Calculate completion percentage

**Example Keep Note:**
```
Feature: User Authentication System

Progress: 75% (6/8 complete)

✅ JWT token generation
✅ Token validation
✅ Password hashing
✅ Login endpoint
✅ Logout endpoint
✅ Token refresh
⬜ Rate limiting
⬜ 2FA support

Last Updated: 2025-11-22 14:45
```

---

### 3. Code Review Checklist

**Use Case:** Ensure code quality before commits

#### Hook: Manual Button → Generate Review Checklist
```yaml
Trigger: User clicks "Review Checklist" button
Action: Create Google Keep checklist for current changes
```

**Implementation:**
- Analyze git diff
- Generate context-aware checklist items
- Create Keep list with unchecked items
- Include file references and line numbers

**Example Keep List:**
```
Code Review: JWT Authentication

⬜ Verify password hashing uses bcrypt
⬜ Check token expiration is configurable
⬜ Ensure error messages don't leak info
⬜ Validate input sanitization (lines 42-48)
⬜ Confirm tests cover edge cases
⬜ Update API documentation
⬜ Check for SQL injection vulnerabilities
⬜ Verify CORS configuration

Files: src/auth/jwt_handler.py, tests/test_auth.py
```

---

### 4. Daily Standup Notes

**Use Case:** Auto-generate standup notes from work activity

#### Hook: On Day End (5:00 PM) → Generate Standup
```yaml
Trigger: Scheduled (daily at 5:00 PM)
Action: Summarize day's work in Google Keep
```

**Implementation:**
- Collect all tasks logged today
- Group by feature/component
- Calculate time spent (from timestamps)
- Generate "Yesterday/Today/Blockers" format

**Example Keep Note:**
```
Standup - 2025-11-22

✅ Yesterday:
- Implemented JWT authentication (3.5 hours)
- Added token validation tests (1.2 hours)
- Fixed security vulnerability in password reset (0.8 hours)

📋 Today:
- Implement rate limiting for auth endpoints
- Add 2FA support
- Update API documentation

🚧 Blockers:
- Need clarification on 2FA provider (Twilio vs. custom)
- Waiting for security review of token storage

📊 Stats: 8 tasks completed, 12 files modified
```

---

### 5. Bug Tracking Integration

**Use Case:** Capture bugs with full context

#### Hook: On Error in Terminal → Create Bug Note
```yaml
Trigger: Error detected in terminal output
Action: Create Google Keep note with error context
```

**Implementation:**
- Capture error message and stack trace
- Include current file and line number
- Add git branch and recent changes
- Attach relevant code snippets

**Example Keep Note:**
```
🐛 Bug: TypeError in JWT validation

Error: 'NoneType' object has no attribute 'decode'
File: src/auth/jwt_handler.py, line 67

Stack Trace:
  File "src/auth/jwt_handler.py", line 67, in validate_token
    payload = jwt.decode(token, SECRET_KEY)
TypeError: 'NoneType' object has no attribute 'decode'

Context:
- Branch: feature/jwt-auth
- Last Modified: 2025-11-22 14:32
- Recent Changes: Added token validation function

Code Snippet (lines 65-70):
def validate_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY)  # Line 67
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token expired")

💡 Possible Cause: Token is None when passed to function
```

---

### 6. Learning Journal

**Use Case:** Capture insights and learnings automatically

#### Hook: On Comment Added → Extract Learning
```yaml
Trigger: Comment added with "TIL:" or "NOTE:" prefix
Action: Add to learning journal in Google Keep
```

**Implementation:**
- Detect special comment patterns
- Extract learning content
- Categorize by topic/technology
- Add to dated learning journal

**Example Keep Note:**
```
Learning Journal - November 2025

📚 Week of Nov 18-22

🔐 Security:
- TIL: JWT tokens should use HS256 or RS256, never "none" algorithm
- TIL: Always validate token expiration on the server side
- NOTE: bcrypt work factor should be 12+ for production

⚡ Performance:
- TIL: SQLite can handle 100k+ reads/sec with proper indexing
- NOTE: LRU cache reduced API response time by 450x

🧪 Testing:
- TIL: pytest-asyncio required for testing async functions
- NOTE: Mock external API calls to avoid flaky tests

📊 Total Learnings This Week: 12
```

---

### 7. Documentation Sync

**Use Case:** Keep documentation in sync with code changes

#### Hook: On File Save → Update Documentation Checklist
```yaml
Trigger: Source file saved
Condition: File has public API or exports
Action: Check if documentation needs updating
```

**Implementation:**
- Detect API changes (new functions, changed signatures)
- Compare with existing documentation
- Create Keep checklist for doc updates
- Link to specific doc sections

**Example Keep List:**
```
Documentation Updates Needed

⬜ Update JWT authentication guide
   - New function: refresh_token() (jwt_handler.py:89)
   - Changed signature: validate_token() now returns dict

⬜ Add API endpoint documentation
   - POST /auth/refresh (routes.py:45)
   - Response format changed for /auth/login

⬜ Update README examples
   - Token expiration now configurable
   - New environment variable: JWT_EXPIRY_HOURS

Files to Update:
- docs/authentication.md
- docs/api-reference.md
- README.md

Auto-detected: 2025-11-22 14:45
```

---

### 8. Meeting Notes Preparation

**Use Case:** Prepare for meetings with context from recent work

#### Hook: Manual Button → Generate Meeting Prep
```yaml
Trigger: User clicks "Prep Meeting Notes"
Action: Create Google Keep note with recent work summary
```

**Implementation:**
- Collect tasks from last N days
- Group by feature/epic
- Identify blockers and questions
- Generate talking points

**Example Keep Note:**
```
Meeting Prep: Sprint Review - 2025-11-22

🎯 Completed This Sprint:

Authentication System (8 tasks)
- JWT token generation and validation
- Password hashing with bcrypt
- Login/logout endpoints
- Token refresh mechanism
- Security: Rate limiting, input validation

Testing Infrastructure (5 tasks)
- 19 unit tests (100% passing)
- Integration tests for auth flow
- Performance benchmarks

📊 Metrics:
- 13 tasks completed
- 24 files modified
- 1,247 lines added
- 0 critical bugs

🚧 Blockers & Questions:
- Need decision on 2FA provider
- Clarify token storage requirements
- Security review pending

💡 Demo Ready:
- Full authentication flow
- Token generation and validation
- Protected API endpoints
```

---

### 9. Code Snippet Library

**Use Case:** Build a searchable library of useful code patterns

#### Hook: On Comment with "SNIPPET:" → Save to Library
```yaml
Trigger: Comment added with "SNIPPET:" tag
Action: Extract code and save to Google Keep library
```

**Implementation:**
- Detect SNIPPET comments
- Extract surrounding code block
- Add metadata (language, file, date)
- Categorize by tags
- Make searchable in Keep

**Example Keep Note:**
```
Code Snippets: Authentication

🔐 JWT Token Generation
Language: Python
File: src/auth/jwt_handler.py
Tags: #jwt #security #authentication

```python
def generate_token(user_id: str, expires_in: int = 3600) -> str:
    """Generate JWT token with expiration"""
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(seconds=expires_in)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")
```

Usage: Call with user_id after successful login
Added: 2025-11-22

---

🔐 Password Hashing
Language: Python
File: src/auth/password.py
Tags: #security #bcrypt #password

```python
def hash_password(password: str) -> str:
    """Hash password using bcrypt with work factor 12"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()
```

Usage: Always hash passwords before storing
Added: 2025-11-22
```

---

### 10. Time Tracking

**Use Case:** Automatic time tracking for tasks and features

#### Hook: On File Save → Track Time Spent
```yaml
Trigger: File save (with idle detection)
Action: Update time tracking in Google Keep
```

**Implementation:**
- Track active coding time (exclude idle)
- Associate time with current task/feature
- Update daily time log
- Generate weekly summaries

**Example Keep Note:**
```
Time Tracking - Week of Nov 18-22

📊 Daily Breakdown:

Monday, Nov 18: 6.5 hours
- Authentication system: 4.2h
- Testing: 1.8h
- Documentation: 0.5h

Tuesday, Nov 19: 7.2 hours
- JWT implementation: 5.1h
- Bug fixes: 1.4h
- Code review: 0.7h

Wednesday, Nov 20: 5.8 hours
- Token validation: 3.2h
- Security hardening: 2.1h
- Meetings: 0.5h

Thursday, Nov 21: 6.9 hours
- Rate limiting: 4.5h
- Integration tests: 1.9h
- Documentation: 0.5h

Friday, Nov 22: 4.3 hours (so far)
- 2FA research: 2.1h
- Bug fixes: 1.7h
- Standup: 0.5h

📈 Weekly Total: 30.7 hours
📁 Most Active: src/auth/ (18.3h)
🎯 Top Feature: Authentication (22.1h)
```

---

## Advanced Patterns

### 11. Context-Aware Task Suggestions

**Hook:** Analyze current work and suggest next tasks

**Implementation:**
- Analyze incomplete features
- Check for missing tests
- Identify documentation gaps
- Suggest logical next steps
- Create Keep note with prioritized suggestions

---

### 12. Dependency Update Tracker

**Hook:** Track when dependencies need updates

**Implementation:**
- Monitor package.json / requirements.txt changes
- Check for security vulnerabilities
- Create Keep checklist for updates
- Link to changelogs and migration guides

---

### 13. Performance Regression Alerts

**Hook:** Alert when performance degrades

**Implementation:**
- Run performance benchmarks on save
- Compare with baseline metrics
- Create Keep note if regression detected
- Include profiling data and suggestions

---

### 14. Collaboration Handoff Notes

**Hook:** Generate handoff notes when switching context

**Implementation:**
- Detect branch switches or long breaks
- Summarize current state
- List pending tasks
- Create Keep note for team visibility

---

### 15. Automated Retrospective

**Hook:** Generate sprint retrospective from activity

**Implementation:**
- Collect all tasks from sprint
- Analyze patterns (blockers, velocity)
- Generate "What went well / What to improve"
- Create Keep note for retro meeting

---

## Implementation Guide

### Setting Up Hooks

1. **Open Kiro Hook UI**
   - Command Palette → "Open Kiro Hook UI"
   - Or use Explorer View → "Agent Hooks" section

2. **Create New Hook**
   - Choose trigger type (save, test, manual, scheduled)
   - Define conditions (file patterns, test results)
   - Write action prompt for Kiro

3. **Action Prompt Template**
```
When this hook triggers:
1. [Describe what to analyze]
2. Use wlater-mcp to [create/update] Google Keep note
3. Format: [specify format]
4. Include: [list required information]
```

### Example Hook Configuration

**Hook Name:** Log Task on Save

**Trigger:** File Save

**Conditions:**
- File pattern: `src/**/*.py`
- Exclude: `**/test_*.py`

**Action Prompt:**
```
Analyze the changes in the saved file:
1. Get git diff to see what changed
2. Generate a concise task description (1 line)
3. Use wlater-mcp to find or create today's note: "Documee MCP - [YYYY-MM-DD]"
4. Append: "✅ [HH:MM] [task description]"
5. Include modified file path
6. Sync changes to Google Keep
```

---

## Best Practices

### 1. Note Naming Conventions
- **Daily logs:** `Project Name - YYYY-MM-DD`
- **Feature tracking:** `Feature: [Feature Name]`
- **Bug reports:** `🐛 Bug: [Short Description]`
- **Learning journal:** `Learning Journal - [Month Year]`
- **Code snippets:** `Code Snippets: [Category]`

### 2. Label Strategy
- Use labels for categorization: `#work`, `#learning`, `#bugs`
- Add project-specific labels: `#documee-mcp`
- Use status labels: `#in-progress`, `#blocked`, `#done`
- Apply labels automatically in hooks

### 3. Keep Notes Organized
- Archive completed daily logs weekly
- Pin active feature notes
- Use colors for priority (Red = urgent, Yellow = important)
- Regular cleanup of old notes

### 4. Performance Considerations
- Batch updates when possible
- Use local caching before syncing
- Avoid hooks on every keystroke
- Debounce rapid file saves

### 5. Privacy & Security
- Don't log sensitive data (passwords, keys, tokens)
- Use placeholders for PII
- Review notes before sharing
- Consider separate Keep accounts for work/personal

---

## Real-World Workflow Examples

### Workflow 1: Solo Developer

**Morning:**
- Manual hook: "Generate Today's Plan" from yesterday's notes
- Review Keep checklist for today's tasks

**During Development:**
- Auto-log tasks on file saves
- Capture learnings with TIL comments
- Track bugs automatically

**End of Day:**
- Scheduled hook: Generate standup notes
- Review time tracking summary
- Plan tomorrow's tasks

---

### Workflow 2: Team Lead

**Sprint Planning:**
- Manual hook: "Generate Sprint Summary" from last sprint
- Create feature tracking notes for new sprint

**Daily:**
- Review team's standup notes (auto-generated)
- Track feature progress across team
- Monitor blockers in Keep

**Sprint Review:**
- Manual hook: "Generate Sprint Review" with metrics
- Automated retrospective note creation

---

### Workflow 3: Open Source Maintainer

**Issue Triage:**
- Auto-create Keep notes for new GitHub issues
- Track issue resolution progress

**Code Review:**
- Generate review checklists for PRs
- Track review comments and follow-ups

**Release Prep:**
- Manual hook: "Generate Release Notes" from commits
- Create release checklist in Keep

---

## Troubleshooting

### Hook Not Triggering
- Check trigger conditions (file patterns)
- Verify hook is enabled
- Check Kiro logs for errors

### Keep Sync Failures
- Verify wlater-mcp credentials
- Check internet connection
- Review sync error messages

### Performance Issues
- Reduce hook frequency
- Optimize action prompts
- Use caching strategies

---

## Future Enhancements

### Potential Integrations
- **GitHub Issues:** Sync Keep notes with GitHub
- **Jira:** Two-way sync with Jira tickets
- **Slack:** Post summaries to Slack channels
- **Calendar:** Schedule tasks from Keep notes
- **Email:** Send daily summaries via email

### Advanced Features
- **AI-powered task prioritization**
- **Automatic time estimation**
- **Burndown chart generation**
- **Team velocity tracking**
- **Predictive blocker detection**

---

## Conclusion

Combining wlater-mcp with Kiro Agent Hooks creates a powerful, automated workflow system that:

✅ **Reduces manual overhead** - Automatic logging and tracking
✅ **Improves knowledge capture** - Never lose insights or learnings
✅ **Enhances team collaboration** - Shared visibility and context
✅ **Boosts productivity** - Focus on coding, not admin tasks
✅ **Provides actionable insights** - Data-driven decision making

Start with simple hooks (task logging on save) and gradually add more sophisticated automations as you discover what works for your workflow.

---

**Next Steps:**
1. Choose 2-3 hooks from this guide to implement first
2. Test with your current project
3. Iterate based on what provides the most value
4. Share successful patterns with your team

Happy automating! 🚀

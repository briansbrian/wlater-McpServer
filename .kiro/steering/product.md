# Product Overview

**wlater MCP Server** is a Model Context Protocol (MCP) server that provides AI assistants with secure, read-only access to Google Keep notes and lists.

## Purpose

Enable users to query, search, and analyze their Google Keep data through natural language interactions with AI assistants while maintaining strict security boundaries.

## Key Features

- **Read-Only Access**: Tier 1 operations only - no modifications or deletions possible
- **Secure Credential Storage**: Master tokens stored in OS-native keyring (Windows Credential Locker, macOS Keychain, Linux Secret Service)
- **Natural Language Queries**: AI assistants can search, filter, and retrieve Keep data
- **List Management**: View todo items with checked/unchecked status
- **Label Support**: Filter and organize notes by labels

## Security Model

The server implements a tiered exposure model:
- **Tier 1 (Implemented)**: Read-only operations - list, search, get note details
- **Tier 2 (Not Exposed)**: Modifications - create, update, archive
- **Tier 3 (Not Exposed)**: Destructive operations - delete, trash

This ensures AI assistants cannot accidentally modify or delete user data.

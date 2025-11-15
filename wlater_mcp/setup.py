"""Interactive setup script for wlater MCP server credentials.

Guides users through credential storage using either automated selenium
authentication or manual credential entry.
"""

import sys
import os
from pathlib import Path

from wlater_mcp.credentials import (
    store_credentials,
    validate_master_token,
    validate_android_id,
    generate_android_id,
    load_credentials,
    get_config_path
)


def run_setup():
    """Run interactive setup to store Google Keep credentials."""
    print("=" * 60)
    print("wlater MCP Server Setup")
    print("=" * 60)
    print()
    
    # Check if credentials already exist
    try:
        email, token, android_id = load_credentials()
        print("⚠️  Existing credentials found!")
        print(f"   Email: {email}")
        print(f"   Config: {get_config_path()}")
        print()
        
        choice = input("Do you want to reconfigure? This will overwrite existing credentials. (y/N): ").strip().lower()
        if choice not in ['y', 'yes']:
            print()
            print("Setup cancelled. Existing credentials preserved.")
            return
        
        print()
        print("Proceeding with reconfiguration...")
        print()
    except (FileNotFoundError, ValueError, KeyError):
        # No existing credentials, continue with setup
        pass
    
    print("This setup will store your Google Keep credentials securely.")
    print("Master token will be stored in your OS keyring.")
    print("Non-sensitive config will be saved to ~/.wlater")
    print()
    
    # Check if 'token' argument was passed for automated mode
    if len(sys.argv) > 1 and sys.argv[1] == 'token':
        # Automated mode - try to import selenium
        try:
            from wlater_mcp.selenium_auth import run_selenium_auth
            
            print("🔄 Starting automated authentication...")
            print("A browser window will open. Please log in to your Google account.")
            print()
            
            result = run_selenium_auth()
            
            if result is None or not isinstance(result, tuple) or len(result) != 3:
                print()
                print("❌ Automated authentication failed")
                print("Please try manual mode: wlater-setup")
                return
            
            email, token, android_id = result
            
            # Ensure all values are strings
            if not isinstance(email, str) or not isinstance(token, str) or not isinstance(android_id, str):
                print()
                print("❌ Invalid credentials format returned")
                print("Please try manual mode: wlater-setup")
                return
            
            print()
            print("✓ Authentication successful!")
            
        except ImportError as e:
            print()
            print("❌ Selenium is not installed.")
            print()
            print("To use automated authentication, install selenium:")
            print("  pip install selenium")
            print()
            print("Or use manual mode instead:")
            print("  wlater-setup")
            return
        except Exception as e:
            print()
            print(f"❌ Error during automated authentication: {e}")
            print("Try manual mode: wlater-setup")
            return
    else:
        # Manual mode
        print("📖 Manual Setup Mode")
        print()
        print("To get your master token, you can:")
        print("  1. Use automated mode: wlater-setup token")
        print("  2. Follow this guide: https://github.com/rukins/gpsoauth-java/blob/b74ebca999d0f5bd38a2eafe3c0d50be552f6385/README.md#receiving-an-authentication-token")
        print("  3. Or see: https://gkeepapi.readthedocs.io/en/latest/#authenticating")
        print()
        
        choice = 'm'
    
        # Manual entry
        email = input("Enter your Google email: ").strip()
        
        if not email:
            print("❌ Error: Email is required.")
            return
        
        print()
        print("Enter your master token (starts with 'aas_et/'):")
        token = input("Master token: ").strip()
        
        if not token:
            print("❌ Error: Master token is required. Please paste your token.")
            return
        
        print()
        print("Enter your android_id (16 hexadecimal characters):")
        print("(Leave blank to generate a random one)")
        android_id = input("Android ID: ").strip()
        
        if not android_id:
            android_id = generate_android_id()
            print(f"Generated android_id: {android_id}")
    
    # Validate credentials
    print()
    print("Validating credentials...")
    
    if not validate_master_token(token):
        print("❌ Invalid token format. Must start with 'aas_et/'")
        return
    
    if not validate_android_id(android_id):
        print("❌ Invalid android_id. Must be 16 hexadecimal characters")
        return
    
    # Store credentials
    try:
        store_credentials(email, token, android_id)
        print()
        print("=" * 60)
        print("✓ Setup complete!")
        print("=" * 60)
        print()
        print(f"✓ Master token stored in OS keyring")
        print(f"✓ Config saved to ~/.wlater")
        print()
        
        print("Next steps:")
        print("  1. Add wlater-mcp to your mcp.json:")
        print()
        print("     For VS Code (.vscode/mcp.json):")
        print('     {')
        print('       "servers": {')
        print('         "wlater": {')
        print('           "command": "python",')
        print('           "args": ["-m", "wlater_mcp.server"]')
        print('         }')
        print('       }')
        print('     }')
        print()
        print("     For Claude Desktop/other MCP clients:")
        print('     {')
        print('       "mcpServers": {')
        print('         "wlater": {')
        print('           "command": "python",')
        print('           "args": ["-m", "wlater_mcp.server"],')
        print('           "disabled": false')
        print('         }')
        print('       }')
        print('     }')
        print("OR YOU CAN COPY THIS CONFIG TO YOUR AI AGENT TO SET UP THE MCP SERVER")
        print()
        
        print("  2. Restart your IDE or reconnect MCP servers")
        print("  3. The server will authenticate automatically using stored credentials")
        print()
        
    except Exception as e:
        print()
        print(f"❌ Error storing credentials: {e}")
        return


if __name__ == "__main__":
    run_setup()

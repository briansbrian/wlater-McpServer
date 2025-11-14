"""Interactive setup script for wlater MCP server credentials.

Guides users through credential storage using either automated selenium
authentication or manual credential entry.
"""

import sys
from pathlib import Path

from credentials import (
    store_credentials,
    validate_master_token,
    validate_android_id,
    generate_android_id
)


def run_setup():
    """Run interactive setup to store Google Keep credentials."""
    print("=" * 60)
    print("wlater MCP Server Setup")
    print("=" * 60)
    print()
    print("This setup will store your Google Keep credentials securely.")
    print("Master token will be stored in your OS keyring.")
    print("Non-sensitive config will be saved to ~/.wlater")
    print()
    
    # Offer selenium or manual entry
    print("Choose credential method:")
    print("  (s) Automated selenium authentication")
    print("  (m) Manual credential entry")
    print()
    
    choice = input("Enter choice [s/m]: ").strip().lower()
    
    if choice == 's':
        # Import and run selenium script
        try:
            # Add Scripts directory to path
            scripts_dir = Path(__file__).parent.parent / "Scripts"
            sys.path.insert(0, str(scripts_dir))
            
            from selenium_get_oauth import run_selenium_auth
            
            print()
            print("Starting automated authentication...")
            print("A browser window will open. Please log in to your Google account.")
            print()
            
            result = run_selenium_auth()
            
            if result is None:
                print()
                print("❌ Selenium authentication failed")
                print("Please try manual entry or check your credentials.")
                return
            
            email, token, android_id = result
            print()
            print("✓ Authentication successful!")
            
        except ImportError as e:
            print()
            print(f"❌ Error: Could not import selenium script: {e}")
            print("Please ensure selenium_get_oauth.py is in the Scripts/ directory.")
            return
        except Exception as e:
            print()
            print(f"❌ Error during selenium authentication: {e}")
            return
    
    elif choice == 'm':
        # Manual entry
        print()
        email = input("Enter your Google email: ").strip()
        
        print()
        print("Enter your master token (starts with 'aas_et/'):")
        print("(You can obtain this using Scripts/selenium_get_oauth.py)")
        token = input("Master token: ").strip()
        
        print()
        print("Enter your android_id (16 hexadecimal characters):")
        print("(Leave blank to generate a random one)")
        android_id = input("Android ID: ").strip()
        
        if not android_id:
            android_id = generate_android_id()
            print(f"Generated android_id: {android_id}")
    
    else:
        print("Invalid choice. Please run setup again.")
        return
    
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
        print("  1. Add wlater MCP server to your Kiro config:")
        print()
        print('     {')
        print('       "mcpServers": {')
        print('         "wlater": {')
        print('           "command": "C:/path/to/wlater-mcp/.venv/Scripts/python.exe",')
        print('           "args": ["C:/path/to/wlater-mcp/src/server.py"],')
        print('           "disabled": false')
        print('         }')
        print('       }')
        print('     }')
        print()
        print("  2. Restart Kiro or reconnect MCP servers")
        print("  3. MCP tools will authenticate automatically using stored credentials")
        print()
        
    except Exception as e:
        print()
        print(f"❌ Error storing credentials: {e}")
        return


if __name__ == "__main__":
    run_setup()

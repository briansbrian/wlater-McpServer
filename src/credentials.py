"""Credential management for Google Keep authentication.

Handles secure storage of master tokens in OS keyring and configuration
data in ~/.wlater file.
"""

import json
import platform
import getpass
from pathlib import Path
from typing import Tuple, Optional

try:
    import keyring
except ImportError:
    raise ImportError(
        "keyring is required. Install it with: pip install keyring"
    )


SERVICE_NAME = "google-keep-token"

# Platform codes for Android ID generation
PLATFORM_CODES = {
    'Windows': '01',
    'Linux':   '02',
    'Darwin':  '03',
    'Java':    '04',
    'FreeBSD': '05',
    'OpenBSD': '06',
    'NetBSD':  '07',
    'SunOS':   '08',
    'AIX':     '09',
    'HP-UX':   '0a',
}


def get_config_path() -> Path:
    """Return path to .wlater config file in user's home directory."""
    return Path.home() / ".wlater"


def encode_base36_to_hex(s: str) -> str:
    """Convert 6-char base-36 string to 8-char hex.
    
    Args:
        s: 6-character string containing only 0-9 and a-z
        
    Returns:
        8-character hexadecimal string
    """
    if len(s) != 6:
        raise ValueError("Input must be exactly 6 characters")
    
    value = 0
    for ch in s:
        if '0' <= ch <= '9':
            digit = ord(ch) - ord('0')
        elif 'a' <= ch <= 'z':
            digit = ord(ch) - ord('a') + 10
        else:
            raise ValueError("Invalid character; only 0-9 and a-z allowed")
        value = value * 36 + digit
    
    return f"{value:08x}"


def generate_android_id() -> str:
    """Generate reversible Android ID based on system and username.
    
    Structure: 776c61 (wlater) + platform_code + encoded_username
    Total: 16 hexadecimal characters
    
    Returns:
        16-character hexadecimal Android ID
    """
    # App prefix for "wlater"
    app_prefix = "776c61"
    
    # Detect platform
    system = platform.system()
    platform_code = PLATFORM_CODES.get(system, '00')
    
    # Get system username
    username = getpass.getuser()
    
    # Normalize username:
    # 1. Take first 8 characters
    # 2. Convert to lowercase
    # 3. Keep only alphanumeric (letters and numbers)
    # 4. Truncate to 6 chars
    # 5. Pad with '0' if less than 6
    normalized = username[:8].lower()
    normalized = ''.join(c for c in normalized if c.isalnum())[:6]
    normalized = normalized.ljust(6, '0')
    
    # Encode username to hex
    username_hex = encode_base36_to_hex(normalized)
    
    # Combine all parts
    android_id = app_prefix + platform_code + username_hex
    
    return android_id


def validate_master_token(token: str) -> bool:
    """Validate that master token follows expected format (starts with aas_et/)."""
    return token.startswith("aas_et/")


def validate_android_id(android_id: str) -> bool:
    """Validate that android_id is exactly 16 hexadecimal characters."""
    if len(android_id) != 16:
        return False
    try:
        int(android_id, 16)
        return True
    except ValueError:
        return False


def store_credentials(email: str, master_token: str, android_id: str) -> None:
    """Store master token in OS keyring and create .wlater config file.
    
    Args:
        email: User's Google email address
        master_token: Google Keep master token (format: aas_et/...)
        android_id: 16-character hexadecimal Android ID
    """
    # Store token in OS keyring
    keyring.set_password(SERVICE_NAME, email, master_token)
    
    # Store non-sensitive config in ~/.wlater
    config = {
        "email": email,
        "android_id": android_id,
        "android_id_platform": platform.system(),
        "android_id_username": getpass.getuser(),
        "last_sync": None,
        "preferences": {}
    }
    
    config_path = get_config_path()
    config_path.write_text(json.dumps(config, indent=2))


def load_credentials() -> Tuple[str, str, str]:
    """Load credentials from config file and keyring.
    
    Returns:
        Tuple of (email, master_token, android_id)
        
    Raises:
        FileNotFoundError: If .wlater config file doesn't exist
        ValueError: If master token not found in keyring
        KeyError: If config file is missing required fields
    """
    # Load config file to get email and android_id
    config_path = get_config_path()
    
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found at {config_path}. Run setup.py first."
        )
    
    config = json.loads(config_path.read_text())
    email = config["email"]
    android_id = config["android_id"]
    
    # Check if platform or username changed (requires android_id regeneration)
    current_platform = platform.system()
    current_username = getpass.getuser()
    
    if (config.get("android_id_platform") != current_platform or 
        config.get("android_id_username") != current_username):
        # Regenerate android_id
        android_id = generate_android_id()
        config["android_id"] = android_id
        config["android_id_platform"] = current_platform
        config["android_id_username"] = current_username
        config_path.write_text(json.dumps(config, indent=2))
    
    # Retrieve master token from keyring
    master_token = keyring.get_password(SERVICE_NAME, email)
    
    if not master_token:
        raise ValueError(
            f"Master token not found in keyring for {email}. Run setup.py first."
        )
    
    return (email, master_token, android_id)

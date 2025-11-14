"""
Selenium script to automate getting oauth_token from Google accounts
and exchange it for a master token
"""
import time
import sys
import platform
import getpass as getpass_module
import msvcrt  # For Windows key detection
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from gpsoauth import exchange_token

def check_for_exit():
    """Check if user pressed ESC to exit"""
    if sys.platform == 'win32':
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\x1b':  # ESC key
                print("\n\n🛑 Process cancelled by user (ESC pressed)")
                print("Exiting...")
                sys.exit(0)
    # For non-Windows systems, we'll handle Ctrl+C naturally

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

def encode_base36_to_hex(s: str) -> str:
    """Convert 6-char base-36 string to 8-char hex"""
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

def generate_android_id():
    """Generate reversible Android ID based on system and username"""
    # App prefix for "wlater"
    app_prefix = "776c61"
    
    # Detect platform
    system = platform.system()
    platform_code = PLATFORM_CODES.get(system, '00')
    
    # Get system username
    username = getpass_module.getuser()
    
    # Normalize username
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
    
    return android_id, system, username, normalized

def get_oauth_token_selenium(email, password):
    """
    Opens browser, auto-fills email/password, and retrieves oauth_token from cookies
    """
    # Initialize Chrome driver with options to avoid automation detection
    print("🚀 Starting Chrome browser...")
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(options=options)
    
    try:
        # Navigate to Google Embedded Setup page (v2/android version more reliable)
        url = "https://accounts.google.com/embedded/setup/v2/android"
        print(f"📍 Navigating to {url}")
        driver.get(url)
        
        # Wait for email field to load
        print("⏳ Waiting for email field...")
        time.sleep(3)
        
        try:
            # Find and fill email field
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']"))
            )
            print(f"📧 Filling in email: {email}")
            email_field.send_keys(email)
            time.sleep(1)
            
            # Click Next button
            next_button = driver.find_element(By.ID, "identifierNext")
            next_button.click()
            print("✓ Clicked Next (email)")
            
            # Wait for password field or captcha
            print("⏳ Waiting for password field...")
            print("⚠️  If you see a CAPTCHA, please solve it in the browser...")
            
            # Extended wait time for captcha solving
            password_field = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']"))
            )
            print("✓ Password field found")
            time.sleep(2)
            
            print("🔑 Filling in password...")
            password_field.send_keys(password)
            time.sleep(1)
            print("✓ Password filled (you may need to click 'Next' manually)")
            
        except Exception as e:
            print(f"⚠️  Could not auto-fill credentials: {e}")
            print("Please fill them in manually in the browser window...")
        
        print("\n" + "="*60)
        print("📝 MANUAL STEPS REQUIRED:")
        print("="*60)
        print("1. If prompted, complete any 2FA verification")
        print("   (e.g., press a number on your phone to confirm it's you)")
        print("2. Click 'I agree' or 'Agree' when you see the terms")
        print("="*60)
        print("\n" + "="*60)
        print("📝 MANUAL STEPS IN BROWSER:")
        print("="*60)
        print("1. Solve any CAPTCHA if it appears")
        print("2. Click 'Next' on the password page (if not already clicked)")
        print("3. If prompted, complete any 2FA verification")
        print("   (e.g., press a number on your phone to confirm it's you)")
        print("4. Click 'I agree' or 'Agree' when you see the terms")
        print("5. ⚠️  IMPORTANT: Wait 5-10 seconds after 'I agree'")
        print("="*60)
        
        # Prompt user to complete login
        print("\n⚠️  DO NOT PRESS ENTER TOO QUICKLY!")
        print("📌 Only press ENTER after:")
        print("   ✓ You clicked 'I agree'")
        print("   ✓ You waited 5-10 seconds for page to load")
        print("   ✓ Page has Loaded for 5-10 seconds after 'I agree'")
        input("\n👉 Ready? Press ENTER to extract token...")
        
        # Give more time for cookies to be set and page to stabilize
        print("⏳ Waiting for cookies to be set...")
        time.sleep(5)
        
        # Check current URL to debug
        current_url = driver.current_url
        print(f"📍 Current URL: {current_url}")
        
        # Get all cookies
        all_cookies = driver.get_cookies()
        
        # Look for oauth_token in cookies from accounts.google.com
        oauth_token = None
        for cookie in all_cookies:
            if cookie['name'] == 'oauth_token' and 'google.com' in cookie['domain']:
                oauth_token = cookie['value']
                break
        
        if oauth_token:
            print("\n✅ SUCCESS! Found oauth_token:")
            print("-" * 60)
            print(oauth_token)
            print("-" * 60)
            
            # Check if it starts with expected prefix
            if oauth_token.startswith('oauth2_4/'):
                print("✓ Token format looks correct (starts with 'oauth2_4/')")
            else:
                print("⚠️  Warning: Token doesn't start with 'oauth2_4/' - this might be incorrect")
            
            print("\n💾 You can now use this token with get_master_token.py")
            return oauth_token
        else:
            print("\n❌ ERROR: Could not find oauth_token in cookies!")
            print("\n🔍 Found these cookies from google.com:")
            for cookie in all_cookies:
                if 'google.com' in cookie['domain']:
                    print(f"  - {cookie['name']}")
            
            print("\n💡 Tips:")
            print("  - Make sure you clicked 'I agree' on the setup page")
            print("  - The page should show 'Setup successful' or similar")
            print("  - Try waiting a bit longer before pressing ENTER")
            return None
            
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    finally:
        # Ask before closing
        input("\n🔍 Browser will close when you press ENTER...")
        driver.quit()
        print("✋ Browser closed")

def get_master_token(email, oauth_token, android_id="deadbeefdeadbeef"):
    """
    Exchange oauth_token for master token using gpsoauth
    """
    print("\n" + "="*60)
    print("🔄 Exchanging OAuth token for Master token...")
    print("="*60)
    
    try:
        response = exchange_token(email, oauth_token, android_id)
        
        # Response is a dict with format: {'Token': 'aas_et/...', 'Auth': '...', ...}
        if isinstance(response, dict) and 'Token' in response:
            master_token = response['Token']
            print("\n✅ SUCCESS! Your master token is:")
            print("-" * 60)
            print(master_token)
            print("-" * 60)
            
            # Check if it starts with expected prefix
            if master_token.startswith('aas_et/'):
                print("✓ Token format looks correct (starts with 'aas_et/')")
            else:
                print("⚠️  Warning: Token doesn't start with 'aas_et/' - this might be incorrect")
            
            print("\n💾 Save this token securely. You'll use it to authenticate with gkeepapi.")
            return master_token
        else:
            # Fallback if response is already a string
            print("\n✅ SUCCESS! Your master token is:")
            print("-" * 60)
            print(response)
            print("-" * 60)
            print("\n💾 Save this token securely. You'll use it to authenticate with gkeepapi.")
            return response
    except Exception as e:
        print(f"\n❌ Error exchanging token: {e}", file=sys.stderr)
        print("Make sure the OAuth token is valid and not expired.", file=sys.stderr)
        print("\nℹ️  OAuth tokens expire quickly (minutes). Try running the script again.", file=sys.stderr)
        return None

def main():
    try:
        print("="*60)
        print("   Google Master Token Generator (Selenium + gpsoauth)")
        print("="*60)
        print("\nThis script will:")
        print("1. Open Chrome browser")
        print("2. Navigate to Google's embedded setup page")
        print("3. Auto-fill your email and password")
        print("4. Wait for you to complete 2FA and click 'I agree'")
        print("5. Extract the oauth_token from cookies")
        print("6. Exchange it for a master token")
        print("\n⚠️  Make sure you have Chrome and ChromeDriver installed!")
        if sys.platform == 'win32':
            print("💡 Press ESC at any time to cancel")
        else:
            print("💡 Press Ctrl+C at any time to cancel")
            print("="*60)
        
        # Generate Android ID
        print("\n" + "="*60)
        print("🔧 Generating Android ID...")
        print("="*60)
        
        try:
            generated_id, system, username, normalized = generate_android_id()
            print(f"\n✓ Detected OS: {system}")
            print(f"✓ System Username: {username}")
            print(f"✓ Normalized: {normalized}")
            print(f"\n📱 Generated Android ID: {generated_id}")
            print("\nStructure breakdown:")
            print(f"  - App prefix (wlater): {generated_id[0:6]}")
            print(f"  - Platform code ({system}): {generated_id[6:8]}")
            print(f"  - Username encoded ({normalized}): {generated_id[8:16]}")
        except Exception as e:
            print(f"⚠️  Error generating Android ID: {e}")
            generated_id = "deadbeefdeadbeef"
            print(f"Using default: {generated_id}")
        
        print("\n" + "="*60)
        
        # Get email first
        check_for_exit()
        email = input("\nEnter your Google email: ").strip()
        check_for_exit()
        if not email:
            print("❌ Email is required!")
            sys.exit(1)
    
        # Prompt for Android ID with validation
        print("\n💡 Press ENTER to use the generated ID, or type your own custom 16-character hex ID")
        
        while True:
            check_for_exit()
            android_id_input = input(f"\nAndroid ID [{generated_id}]: ").strip()
            check_for_exit()
            android_id = android_id_input if android_id_input else generated_id
            
            # Validate Android ID format
            if len(android_id) != 16:
                print(f"❌ Invalid Android ID! Must be exactly 16 characters (got {len(android_id)})")
                print("   Press Enter to use generated ID, or enter a valid 16-character hex ID")
                continue
            
            # Check if all characters are valid hexadecimal
            try:
                int(android_id, 16)  # This will raise ValueError if not valid hex
                break  # Valid Android ID
            except ValueError:
                print("❌ Invalid Android ID! Must contain only hexadecimal characters (0-9, a-f)")
                print("   Press Enter to use generated ID, or enter a valid hex ID")
                continue
        
        print(f"\n✓ Using Android ID: {android_id}")
        
        check_for_exit()
        input("\n⚠️  Browser will open. You'll need to click 'Next' after password is filled.\nPress ENTER to start...")
        check_for_exit()
        
        # Get password just before opening browser (more secure)
        password = getpass_module.getpass("\nEnter your Google password: ").strip()
        check_for_exit()
        if not password:
            print("❌ Password is required!")
            sys.exit(1)
        
        oauth_token = get_oauth_token_selenium(email, password)
        
        if oauth_token:
            # Exchange for master token
            master_token = get_master_token(email, oauth_token, android_id)
            
            if master_token:
                print("\n" + "="*60)
                print("✅ COMPLETE! You now have your master token.")
                print("="*60)
            else:
                print("\n" + "="*60)
                print("❌ Failed to get master token")
                print("="*60)
                sys.exit(1)
        else:
            print("\n" + "="*60)
            print("❌ Failed to retrieve oauth_token")
            print("Try again or use manual method from AUTH_INSTRUCTIONS.md")
            print("="*60)
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n🛑 Process cancelled by user (Ctrl+C)")
        print("Exiting...")
        sys.exit(0)

if __name__ == "__main__":
    main()

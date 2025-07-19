import os
import time
import threading
import wave
import numpy as np
import sounddevice as sd
from datetime import datetime, timedelta
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.audio import MIMEAudio
from email.mime.text import MIMEText
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import tempfile
import shutil
import uuid

class DoneTalkingBot:
    def __init__(self, config_file="bot_config.json"):
        """
        Initialize the Done-Talking bot
        """
        self.config = self.load_config(config_file)
        self.is_recording = False
        self.audio_data = []
        self.sample_rate = 44100
        self.channels = 2
        self.meeting_active = False
        self.driver = None
        self.meet_service = None
        self.temp_profile_dir = None
        
        # Initialize Google Meet API
        self.setup_google_meet_api()
        
    def load_config(self, config_file):
        """Load configuration from JSON file"""
        default_config = {
            "google_credentials_file": "credentials.json",
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "your_email@gmail.com",
                "password": "your_app_password"
            },
            "audio_settings": {
                "sample_rate": 44100,
                "channels": 2,
                "chunk_size": 1024
            },
            "meeting_check_interval": 10,  # seconds
            "chrome_profile_path": None,  # Will be auto-detected
            "use_fresh_profile": True,  # Use temporary profile to avoid conflicts
            "auto_join_delay": 3  # seconds to wait before auto-joining
        }
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except FileNotFoundError:
            print(f"Config file {config_file} not found, creating default...")
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config
    
    def setup_google_meet_api(self):
        """Setup Google Meet API authentication"""
        # Check if credentials file exists
        if not os.path.exists(self.config['google_credentials_file']):
            print(f"❌ Google credentials file '{self.config['google_credentials_file']}' not found!")
            print("\n📋 To set up Google Meet API:")
            print("1. Go to https://console.cloud.google.com/")
            print("2. Create a new project or select existing one")
            print("3. Enable the Google Meet API")
            print("4. Go to 'Credentials' → 'Create Credentials' → 'OAuth 2.0 Client ID'")
            print("5. Choose 'Desktop Application'")
            print("6. Download the JSON file and save as 'credentials.json'")
            print("7. Make sure to add your email to test users if in development mode")
            print("\n⚠️  For now, the bot will run without Google Meet API integration")
            print("   You can still use manual recording mode!")
            self.meet_service = None
            return
            
        try:
            SCOPES = ['https://www.googleapis.com/auth/meetings.space.created']
            
            creds = None
            # Token file stores the user's access and refresh tokens
            if os.path.exists('token.pickle'):
                with open('token.pickle', 'rb') as token:
                    creds = pickle.load(token)
            
            # If there are no valid credentials, let the user log in
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.config['google_credentials_file'], SCOPES)
                    creds = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open('token.pickle', 'wb') as token:
                    pickle.dump(creds, token)
            
            self.meet_service = build('meet', 'v2', credentials=creds)
            print("✅ Google Meet API initialized successfully!")
            
        except Exception as e:
            print(f"❌ Error setting up Google Meet API: {str(e)}")
            print("⚠️  Bot will run without API integration")
            self.meet_service = None
    
    def get_chrome_profile_path(self):
        """Auto-detect Chrome profile path based on OS"""
        import platform
        
        system = platform.system()
        username = os.getenv('USERNAME') or os.getenv('USER')
        
        if system == "Windows":
            return f"C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data"
        elif system == "Darwin":  # macOS
            return f"/Users/{username}/Library/Application Support/Google/Chrome"
        elif system == "Linux":
            return f"/home/{username}/.config/google-chrome"
        else:
            return None
    
    def create_temp_profile(self):
        """Create a temporary Chrome profile directory"""
        try:
            # Create temporary directory
            self.temp_profile_dir = tempfile.mkdtemp(prefix="chrome_profile_")
            print(f"🔧 Created temporary Chrome profile: {self.temp_profile_dir}")
            return self.temp_profile_dir
        except Exception as e:
            print(f"❌ Failed to create temp profile: {e}")
            return None
    
    def kill_existing_chrome_processes(self):
        """Kill existing Chrome processes that might be using the profile"""
        import subprocess
        import platform
        
        try:
            system = platform.system()
            if system == "Windows":
                subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], 
                             capture_output=True, check=False)
            elif system in ["Linux", "Darwin"]:
                subprocess.run(["pkill", "-f", "chrome"], 
                             capture_output=True, check=False)
            
            print("🔄 Killed existing Chrome processes")
            time.sleep(2)  # Wait for processes to fully terminate
            
        except Exception as e:
            print(f"⚠️  Could not kill Chrome processes: {e}")
    
    def setup_browser(self, use_profile=True):
        """Setup Chrome browser for Google Meet automation with better error handling"""
        chrome_options = Options()
        
        # Kill existing Chrome processes first if using profile
        if use_profile and not self.config.get('use_fresh_profile', True):
            print("🔄 Attempting to kill existing Chrome processes...")
            self.kill_existing_chrome_processes()
        
        # Handle profile setup
        if use_profile:
            if self.config.get('use_fresh_profile', True):
                # Use temporary profile to avoid conflicts
                profile_path = self.create_temp_profile()
                if profile_path:
                    chrome_options.add_argument(f"--user-data-dir={profile_path}")
                    print(f"🔧 Using temporary Chrome profile")
                else:
                    print("⚠️  Failed to create temp profile, using default")
            else:
                # Use existing profile with conflict handling
                profile_path = self.config.get('chrome_profile_path') or self.get_chrome_profile_path()
                if profile_path and os.path.exists(profile_path):
                    # Add unique identifier to avoid conflicts
                    unique_id = str(uuid.uuid4())[:8]
                    temp_profile = f"{profile_path}_bot_{unique_id}"
                    
                    try:
                        # Copy existing profile to temp location
                        if not os.path.exists(temp_profile):
                            shutil.copytree(profile_path, temp_profile, ignore_errors=True)
                        
                        chrome_options.add_argument(f"--user-data-dir={temp_profile}")
                        self.temp_profile_dir = temp_profile
                        print(f"🔧 Using copied Chrome profile: {temp_profile}")
                    except Exception as e:
                        print(f"⚠️  Could not copy profile, using fresh session: {e}")
                        profile_path = self.create_temp_profile()
                        if profile_path:
                            chrome_options.add_argument(f"--user-data-dir={profile_path}")
                else:
                    print("⚠️  Chrome profile not found, using fresh browser session")
                    profile_path = self.create_temp_profile()
                    if profile_path:
                        chrome_options.add_argument(f"--user-data-dir={profile_path}")
        
        # Essential options for automation
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")  # Speed up loading
        chrome_options.add_argument("--mute-audio")  # Prevent feedback
        
        # Prevent Chrome from showing "Chrome is being controlled" banner
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Media permissions - auto-allow microphone and camera
        chrome_options.add_argument("--use-fake-ui-for-media-stream")
        chrome_options.add_argument("--use-fake-device-for-media-stream")
        
        # Add permissions for microphone and camera
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.media_stream_mic": 1,
            "profile.default_content_setting_values.media_stream_camera": 1,
            "profile.default_content_setting_values.notifications": 1,
            "profile.managed_default_content_settings.images": 2  # Block images
        })
        
        # Try multiple times with different strategies
        for attempt in range(3):
            try:
                print(f"🔄 Chrome setup attempt {attempt + 1}/3")
                
                if attempt == 1:
                    # Second attempt: try headless mode
                    print("🔧 Trying headless mode...")
                    chrome_options.add_argument("--headless=new")
                    chrome_options.add_argument("--disable-gpu")
                elif attempt == 2:
                    # Third attempt: minimal options
                    print("🔧 Trying minimal configuration...")
                    chrome_options = Options()
                    chrome_options.add_argument("--no-sandbox")
                    chrome_options.add_argument("--disable-dev-shm-usage")
                    temp_dir = self.create_temp_profile()
                    if temp_dir:
                        chrome_options.add_argument(f"--user-data-dir={temp_dir}")
                
                self.driver = webdriver.Chrome(options=chrome_options)
                
                # Execute script to hide automation detection
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                print(f"✅ Chrome driver setup successful on attempt {attempt + 1}")
                return self.driver
                
            except Exception as e:
                print(f"❌ Chrome setup attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    time.sleep(2)
                    # Clean up failed attempt
                    try:
                        if hasattr(self, 'driver') and self.driver:
                            self.driver.quit()
                    except:
                        pass
                    self.driver = None
        
        print("❌ Failed to setup Chrome driver after all attempts")
        print("\n💡 Troubleshooting suggestions:")
        print("1. Make sure Chrome is completely closed before running the bot")
        print("2. Try running: pkill -f chrome  (Linux/Mac) or taskkill /f /im chrome.exe (Windows)")
        print("3. Set 'use_fresh_profile': true in your config file")
        print("4. Make sure ChromeDriver is properly installed and in PATH")
        return None
    
    def find_element_by_multiple_strategies(self, selectors_dict, timeout=10):
        """Try multiple strategies to find an element"""
        strategies = [
            ('css', selectors_dict.get('css', [])),
            ('xpath', selectors_dict.get('xpath', [])),
            ('text', selectors_dict.get('text', []))
        ]
        
        for strategy_type, selectors in strategies:
            if not selectors:
                continue
                
            for selector in selectors:
                try:
                    if strategy_type == 'css':
                        element = WebDriverWait(self.driver, timeout).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        return element
                    elif strategy_type == 'xpath':
                        element = WebDriverWait(self.driver, timeout).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        return element
                    elif strategy_type == 'text':
                        # Find by text content
                        element = WebDriverWait(self.driver, timeout).until(
                            EC.presence_of_element_located((By.XPATH, f"//*[contains(text(), '{selector}')]"))
                        )
                        return element
                except TimeoutException:
                    continue
        return None
    
    def click_element_multiple_strategies(self, selectors_dict, timeout=10):
        """Try multiple strategies to find and click an element"""
        strategies = [
            ('css', selectors_dict.get('css', [])),
            ('xpath', selectors_dict.get('xpath', [])),
            ('text', selectors_dict.get('text', []))
        ]
        
        for strategy_type, selectors in strategies:
            if not selectors:
                continue
                
            for selector in selectors:
                try:
                    if strategy_type == 'css':
                        element = WebDriverWait(self.driver, timeout).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    elif strategy_type == 'xpath':
                        element = WebDriverWait(self.driver, timeout).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    elif strategy_type == 'text':
                        element = WebDriverWait(self.driver, timeout).until(
                            EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(), '{selector}')]"))
                        )
                    
                    # Try multiple click methods
                    click_methods = [
                        lambda: element.click(),
                        lambda: self.driver.execute_script("arguments[0].click();", element),
                        lambda: ActionChains(self.driver).click(element).perform(),
                        lambda: element.send_keys(Keys.RETURN)
                    ]
                    
                    for click_method in click_methods:
                        try:
                            click_method()
                            print(f"✅ Successfully clicked element using {strategy_type} selector: {selector}")
                            return True
                        except Exception as click_error:
                            print(f"⚠️  Click method failed: {click_error}")
                            continue
                    
                except TimeoutException:
                    continue
                except Exception as e:
                    print(f"⚠️  Error with {strategy_type} selector '{selector}': {e}")
                    continue
        return False
    
    def auto_join_meeting(self, user_name="Done-Talking Bot", max_wait_time=30):
        """
        Improved auto-join with comprehensive button detection
        """
        print(f"🤖 Auto-joining meeting as '{user_name}'...")
        
        # Wait for page to stabilize
        time.sleep(self.config.get('auto_join_delay', 3))
        
        try:
            # Step 1: Handle name input if present
            name_selectors = {
                'css': [
                    "input[placeholder*='name' i]",
                    "input[placeholder*='Name']", 
                    "input[aria-label*='name' i]",
                    "input[aria-label*='Name']",
                    ".whsOnd input",
                    "[jsname='YPqjbf'] input",
                    "input[type='text']"
                ],
                'xpath': [
                    "//input[contains(@placeholder, 'name')]",
                    "//input[contains(@placeholder, 'Name')]",
                    "//input[contains(@aria-label, 'name')]",
                    "//input[contains(@aria-label, 'Name')]"
                ]
            }
            
            name_element = self.find_element_by_multiple_strategies(name_selectors, timeout=5)
            if name_element:
                try:
                    # Clear and enter name
                    name_element.clear()
                    time.sleep(0.5)
                    name_element.send_keys(user_name)
                    time.sleep(0.5)
                    print(f"📝 Name entered: {user_name}")
                except Exception as e:
                    print(f"⚠️  Could not enter name: {e}")
            else:
                print("📝 Name input not found (might already be set)")
            
            # Step 2: Disable camera and microphone
            self.disable_camera_and_mic_improved()
            
            # Step 3: Find and click join button with comprehensive selectors
            print("🔘 Looking for join button...")
            
            join_button_selectors = {
                'css': [
                    # Primary Google Meet join button selectors
                    "[jsname='Qx7uuf']",
                    ".VfPpkd-LgbsSe[jsname='Qx7uuf']",
                    "button[aria-label*='Join' i]",
                    "button[aria-label*='join' i]",
                    "[data-mdc-dialog-action='ok']",
                    ".uArJ5e .VfPpkd-LgbsSe",
                    "button[role='button'][aria-label*='Join' i]",
                    ".VfPpkd-LgbsSe.VfPpkd-LgbsSe-OWXEXe-k8QpJ",
                    "[role='button'].VfPpkd-LgbsSe",
                    "div[role='button'][jsname='Qx7uuf']",
                    # Alternative selectors
                    "button:contains('Join now')",
                    "button:contains('Ask to join')",
                    "[aria-label*='Join now' i]",
                    "[aria-label*='Ask to join' i]"
                ],
                'xpath': [
                    # XPath selectors for join buttons
                    "//button[contains(@aria-label, 'Join')]",
                    "//button[contains(@aria-label, 'join')]",
                    "//div[@role='button' and contains(@aria-label, 'Join')]",
                    "//div[@role='button' and contains(@aria-label, 'join')]",
                    "//*[@jsname='Qx7uuf']",
                    "//button[contains(text(), 'Join now')]",
                    "//button[contains(text(), 'Ask to join')]",
                    "//div[contains(text(), 'Join now')]",
                    "//div[contains(text(), 'Ask to join')]",
                    "//*[contains(@class, 'VfPpkd-LgbsSe') and contains(@aria-label, 'Join')]"
                ],
                'text': [
                    'Join now',
                    'Ask to join',
                    'Join',
                    'Continue'
                ]
            }
            
            # Try to click join button
            if self.click_element_multiple_strategies(join_button_selectors, timeout=15):
                print("✅ Join button clicked successfully!")
                time.sleep(3)  # Wait for join process
                return True
            else:
                print("❌ Could not find or click join button")
                self.debug_join_buttons()
                return False
                
        except Exception as e:
            print(f"❌ Error during auto-join: {e}")
            return False
    
    def debug_join_buttons(self):
        """Debug function to help identify join buttons"""
        try:
            print("\n🔍 DEBUG: Searching for potential join buttons...")
            
            # Find all buttons
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            divs_with_role_button = self.driver.find_elements(By.XPATH, "//div[@role='button']")
            
            all_clickable = buttons + divs_with_role_button
            
            print(f"Found {len(all_clickable)} clickable elements:")
            
            for i, element in enumerate(all_clickable[:15]):  # Limit output
                try:
                    tag_name = element.tag_name
                    text = element.text.strip()
                    aria_label = element.get_attribute("aria-label") or ""
                    classes = element.get_attribute("class") or ""
                    jsname = element.get_attribute("jsname") or ""
                    
                    if any(keyword in (text + aria_label).lower() for keyword in ['join', 'continue', 'ok']):
                        print(f"  🎯 POTENTIAL MATCH {i+1}: <{tag_name}>")
                        print(f"     Text: '{text}'")
                        print(f"     Aria-label: '{aria_label}'")
                        print(f"     Classes: '{classes[:100]}...' " if len(classes) > 100 else f"     Classes: '{classes}'")
                        if jsname:
                            print(f"     JSName: '{jsname}'")
                        print()
                
                except Exception as e:
                    continue
            
            # Also check for specific Google Meet elements
            specific_elements = self.driver.find_elements(By.CSS_SELECTOR, "[jsname], .VfPpkd-LgbsSe")
            print(f"\nFound {len(specific_elements)} elements with Google Meet signatures")
            
        except Exception as e:
            print(f"Debug failed: {e}")
    
    def disable_camera_and_mic_improved(self):
        """Improved camera and microphone disabling with more selectors"""
        try:
            print("🔧 Disabling camera and microphone...")
            
            # Camera selectors (more comprehensive)
            camera_selectors = {
                'css': [
                    "[aria-label*='Turn off camera' i]",
                    "[aria-label*='camera' i][data-is-muted='false']",
                    "[aria-label*='camera' i]:not([data-is-muted='true'])",
                    "button[aria-label*='camera' i]",
                    ".google-material-icons[data-icon*='videocam']",
                    "[jsname='BOHaEe']",
                    "[data-tooltip*='camera' i]",
                    "div[role='button'][aria-label*='camera' i]"
                ],
                'xpath': [
                    "//button[contains(@aria-label, 'camera') and not(contains(@aria-label, 'off'))]",
                    "//div[@role='button' and contains(@aria-label, 'camera') and not(contains(@aria-label, 'off'))]",
                    "//*[@jsname='BOHaEe']"
                ]
            }
            
            if self.click_element_multiple_strategies(camera_selectors, timeout=3):
                print("📹 Camera disabled successfully")
            else:
                print("📹 Camera control not found (may already be off)")
            
            time.sleep(1)
            
            # Microphone selectors (more comprehensive)
            mic_selectors = {
                'css': [
                    "[aria-label*='Turn off microphone' i]",
                    "[aria-label*='microphone' i][data-is-muted='false']",
                    "[aria-label*='microphone' i]:not([data-is-muted='true'])",
                    "button[aria-label*='microphone' i]",
                    ".google-material-icons[data-icon*='mic']",
                    "[jsname='r8qRAd']",
                    "[data-tooltip*='microphone' i]",
                    "div[role='button'][aria-label*='microphone' i]"
                ],
                'xpath': [
                    "//button[contains(@aria-label, 'microphone') and not(contains(@aria-label, 'off'))]",
                    "//div[@role='button' and contains(@aria-label, 'microphone') and not(contains(@aria-label, 'off'))]",
                    "//*[@jsname='r8qRAd']"
                ]
            }
            
            if self.click_element_multiple_strategies(mic_selectors, timeout=3):
                print("🎤 Microphone disabled successfully")
            else:
                print("🎤 Microphone control not found (may already be off)")
                
        except Exception as e:
            print(f"⚠️  Error disabling camera/mic: {e}")
    
    def join_meeting_improved(self, meeting_url, user_name="Done-Talking Bot", max_retries=3):
        """
        Improved meeting join with better auto-join functionality
        """
        print(f"🔗 Attempting to join meeting: {meeting_url}")
        
        for attempt in range(max_retries):
            print(f"📝 Attempt {attempt + 1} of {max_retries}")
            
            if not self.driver:
                if not self.setup_browser():
                    print("❌ Failed to setup browser")
                    if attempt == max_retries - 1:
                        return False
                    continue
            
            try:
                # Navigate to meeting with retry
                for nav_attempt in range(3):
                    try:
                        self.driver.get(meeting_url)
                        print("📄 Page loaded successfully")
                        break
                    except WebDriverException as e:
                        print(f"⚠️  Navigation attempt {nav_attempt + 1} failed: {e}")
                        if nav_attempt == 2:
                            raise
                        time.sleep(2)
                
                # Wait for page to fully load
                time.sleep(5)
                
                # Check current page state
                page_title = self.driver.title.lower()
                current_url = self.driver.current_url
                print(f"📍 Current page: {page_title}")
                print(f"🌐 Current URL: {current_url}")
                
                # Look for error messages first
                error_selectors = [
                    "//*[contains(text(), \"can't join\")]",
                    ".error-message",
                    "[role='alert']",
                    ".VfPpkd-Bz112c-LgbsSe"
                ]
                
                for selector in error_selectors:
                    try:
                        if selector.startswith("//"):
                            error_elements = self.driver.find_elements(By.XPATH, selector)
                        else:
                            error_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        
                        if error_elements:
                            error_text = error_elements[0].text
                            print(f"❌ Error detected: {error_text}")
                            if "can't join" in error_text.lower():
                                print("🔒 Meeting is restricted. Trying alternative approach...")
                                return self.handle_restricted_meeting(meeting_url, user_name)
                    except:
                        continue
                
                # Check if already in meeting
                meeting_indicators = [
                    "[data-meeting-state]",
                    ".google-material-icons[data-icon='call_end']",
                    "[aria-label*='Leave call']",
                    ".VLoCzf",
                    "[jsname='HiaYvf']"
                ]
                
                for selector in meeting_indicators:
                    if self.driver.find_elements(By.CSS_SELECTOR, selector):
                        print("✅ Already in meeting!")
                        self.meeting_active = True
                        return True
                
                # AUTO-JOIN: This is the key improvement
                if self.auto_join_meeting(user_name):
                    # Check if we successfully joined
                    time.sleep(5)  # Wait for join process
                    if self.check_meeting_status():
                        print("✅ Successfully joined the meeting!")
                        self.meeting_active = True
                        return True
                    else:
                        print("⏳ Waiting for admission or processing...")
                        if self.wait_for_admission():
                            print("✅ Successfully joined after admission!")
                            self.meeting_active = True
                            return True
                else:
                    print("❌ Auto-join failed")
                    continue
                
            except WebDriverException as e:
                print(f"❌ WebDriver error on attempt {attempt + 1}: {e}")
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None
                time.sleep(2)
                
            except Exception as e:
                print(f"❌ Unexpected error on attempt {attempt + 1}: {e}")
                time.sleep(2)
        
        print("❌ Failed to join meeting after all attempts")
        return False
    
    def handle_restricted_meeting(self, meeting_url, user_name):
        """Handle case where meeting is restricted"""
        print("🔒 Meeting is restricted. Trying alternative approaches...")
        
        # Strategy 1: Try with different URL format
        if "/join/" not in meeting_url:
            alt_url = meeting_url.replace("meet.google.com/", "meet.google.com/join/")
            print(f"🔄 Trying alternative URL: {alt_url}")
            try:
                self.driver.get(alt_url)
                time.sleep(3)
                return self.attempt_join_flow(user_name)
            except:
                pass
        
        # Strategy 2: Request admission
        print("📧 Meeting requires admission. Looking for 'Ask to join' option...")
        ask_join_selectors = [
            "button[aria-label*='Ask to join']",
            "button:contains('Ask to join')",
            "[role='button']:contains('Request')",
            ".VfPpkd-LgbsSe:contains('Ask')"
        ]
        
        if self.wait_and_click_element(ask_join_selectors, timeout=5):
            print("✅ Admission requested!")
            return self.wait_for_admission(timeout=300)  # 5 minutes
        
        print("❌ Could not request admission")
        return False
    
    def attempt_join_flow(self, user_name):
        """Attempt the standard join flow"""
        # Enter name if needed
        name_element = self.wait_and_find_element([
            "input[placeholder*='name']", 
            "input[aria-label*='name']"
        ], timeout=3)
        
        if name_element:
            try:
                name_element.clear()
                name_element.send_keys(user_name)
            except:
                pass
        
        # Disable camera/mic
        self.disable_camera_and_mic()
        
        # Click join
        join_selectors = [
            "[jsname='Qx7uuf']",
            "button[aria-label*='Join']",
            "[data-mdc-dialog-action='ok']"
        ]
        
        if self.wait_and_click_element(join_selectors, timeout=10):
            time.sleep(3)
            return self.check_meeting_status()
        
        return False
    
    def disable_camera_and_mic(self):
        """Disable camera and microphone with multiple selectors"""
        try:
            # Camera selectors
            camera_selectors = [
                "[data-is-muted='false'][aria-label*='camera' i]",
                "[aria-label*='Turn off camera' i]",
                "[aria-label*='camera' i]:not([data-is-muted='true'])",
                "button[aria-label*='camera' i]",
                ".google-material-icons[data-icon*='videocam']",
                "[jsname='BOHaEe']"
            ]
            
            if self.wait_and_click_element(camera_selectors, timeout=3):
                print("📹 Camera disabled")
            else:
                print("📹 Camera control not found (may already be off)")
            
            time.sleep(1)
            
            # Microphone selectors  
            mic_selectors = [
                "[data-is-muted='false'][aria-label*='microphone' i]",
                "[aria-label*='Turn off microphone' i]",
                "[aria-label*='microphone' i]:not([data-is-muted='true'])",
                "button[aria-label*='microphone' i]",
                ".google-material-icons[data-icon*='mic']",
                "[jsname='r8qRAd']"
            ]
            
            if self.wait_and_click_element(mic_selectors, timeout=3):
                print("🎤 Microphone disabled")
            else:
                print("🎤 Microphone control not found (may already be off)")
                
        except Exception as e:
            print(f"⚠️  Could not disable camera/mic: {e}")
    
    def check_meeting_status(self):
        """Check if we're successfully in the meeting"""
        meeting_indicators = [
            "[data-meeting-state]",
            ".google-material-icons[data-icon='call_end']",
            "[aria-label*='Leave call']",
            "[aria-label*='End call']",
            ".VLoCzf",
            "[jsname='HiaYvf']"
        ]
        
        for selector in meeting_indicators:
            if self.driver.find_elements(By.CSS_SELECTOR, selector):
                return True
        
        return False
    
    def wait_for_admission(self, timeout=300):
        """Wait for host admission with better status detection and fixed XPath"""
        print("⏳ Waiting for host admission...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check if we're in the meeting
                if self.check_meeting_status():
                    print("✅ Admitted to meeting!")
                    return True
                
                # Check for waiting messages using proper XPath syntax
                waiting_indicators = [
                    "//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'waiting')]",
                    "//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'ask the host')]", 
                    "//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'admit')]",
                    "//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'permission')]"
                ]
                
                # Also check with CSS selectors
                css_waiting_indicators = [
                    ".CwaK9",
                    "[role='status']",
                    ".waiting-message",
                    ".admission-message"
                ]
                
                is_waiting = False
                
                # Try XPath first
                for xpath in waiting_indicators:
                    try:
                        elements = self.driver.find_elements(By.XPATH, xpath)
                        if elements:
                            print(f"⏳ Status: {elements[0].text}")
                            is_waiting = True
                            break
                    except Exception:
                        continue
                
                # Try CSS selectors if XPath didn't work
                if not is_waiting:
                    for css_sel in css_waiting_indicators:
                        try:
                            elements = self.driver.find_elements(By.CSS_SELECTOR, css_sel)
                            if elements:
                                text = elements[0].text.lower()
                                if any(word in text for word in ['waiting', 'admit', 'permission', 'host']):
                                    print(f"⏳ Status: {elements[0].text}")
                                    is_waiting = True
                                    break
                        except Exception:
                            continue
                
                if not is_waiting:
                    # Check for error messages using proper XPath
                    error_elements = self.driver.find_elements(
                        By.XPATH, 
                        "//div[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), \"can't join\")]"
                    )
                    if error_elements:
                        print("❌ Access denied - meeting may be restricted")
                        return False
                
                time.sleep(5)
                
            except Exception as e:
                print(f"⚠️  Error while waiting: {e}")
                time.sleep(5)
        
        print("⏰ Timeout waiting for admission")
        return False
    
    # Keep all other methods unchanged (audio recording, processing, etc.)
    def start_audio_recording(self):
        """Start recording system audio"""
        print("🎤 Starting audio recording...")
        self.is_recording = True
        self.audio_data = []
        
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio callback status: {status}")
            if self.is_recording:
                self.audio_data.append(indata.copy())
        
        try:
            # Start recording in a separate thread
            self.stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=audio_callback,
                blocksize=1024
            )
            self.stream.start()
            print("✅ Audio recording started!")
        except Exception as e:
            print(f"❌ Failed to start audio recording: {e}")
            self.is_recording = False
    
    def stop_audio_recording(self):
        """Stop recording and save audio file"""
        if not self.is_recording:
            return None
            
        print("🛑 Stopping audio recording...")
        self.is_recording = False
        
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()
        
        if not self.audio_data:
            print("📭 No audio data recorded")
            return None
        
        # Combine all audio chunks
        audio_array = np.concatenate(self.audio_data, axis=0)
        
        # Save to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"meeting_recording_{timestamp}.wav"
        
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.sample_rate)
                wf.writeframes((audio_array * 32767).astype(np.int16).tobytes())
            
            print(f"💾 Audio saved as: {filename}")
            return filename
        except Exception as e:
            print(f"❌ Failed to save audio: {e}")
            return None
    
    def monitor_meeting_status(self):
        """Monitor if meeting is still active"""
        while self.meeting_active:
            try:
                if not self.driver:
                    break
                    
                # Check if we're still in meeting
                if not self.check_meeting_status():
                    print("📞 Meeting appears to have ended")
                    self.meeting_active = False
                    break
                    
                time.sleep(self.config['meeting_check_interval'])
                
            except Exception as e:
                print(f"⚠️  Error monitoring meeting: {str(e)}")
                break
    
    def process_audio_pipeline(self, audio_file):
        """Process audio through pipeline (placeholder)"""
        print(f"🔄 Processing audio file: {audio_file}")
        
        try:
            # Placeholder for actual processing
            processed_file = f"processed_{audio_file}"
            
            # Dummy processing (replace with your actual pipeline)
            import shutil
            shutil.copy(audio_file, processed_file)
            
            return {
                'processed_file': processed_file,
                'transcript': "Sample transcript would go here",
                'summary': "Sample summary would go here",
                'duration': "45 minutes",
                'speakers': 3
            }
            
        except Exception as e:
            print(f"❌ Error processing audio: {str(e)}")
            return None
    
    def send_results_email(self, results, recipient_email):
        """Send processed results via email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config['email']['username']
            msg['To'] = recipient_email
            msg['Subject'] = f"Done-Talking: Meeting Summary - {datetime.now().strftime('%Y-%m-%d')}"
            
            body = f"""
Hello!

Your meeting has been processed by Done-Talking bot. Here are the results:

📊 Meeting Statistics:
- Duration: {results['duration']}
- Speakers Detected: {results['speakers']}

📝 Summary:
{results['summary']}

🎵 The processed audio summary is attached to this email.

Best regards,
Done-Talking Bot
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach processed audio file
            if os.path.exists(results['processed_file']):
                with open(results['processed_file'], 'rb') as f:
                    audio_attachment = MIMEAudio(f.read())
                    audio_attachment.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{os.path.basename(results["processed_file"])}"'
                    )
                    msg.attach(audio_attachment)
            
            # Send email
            server = smtplib.SMTP(self.config['email']['smtp_server'], self.config['email']['smtp_port'])
            server.starttls()
            server.login(self.config['email']['username'], self.config['email']['password'])
            server.sendmail(self.config['email']['username'], recipient_email, msg.as_string())
            server.quit()
            
            print(f"📧 Results sent to {recipient_email}")
            return True
            
        except Exception as e:
            print(f"❌ Error sending email: {str(e)}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        if self.is_recording:
            self.stop_audio_recording()
        
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        
        self.meeting_active = False
    
    def run_meeting_session(self, meeting_url, host_email):
        """Complete workflow: Join meeting, record, process, and send results"""
        print("🤖 Done-Talking Bot Starting...")
        
        try:
            # Join meeting with improved method
            if not self.join_meeting_improved(meeting_url):
                print("❌ Failed to join meeting")
                return False
            
            # Start recording
            self.start_audio_recording()
            
            # Monitor meeting in separate thread
            monitor_thread = threading.Thread(target=self.monitor_meeting_status)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            print("📹 Recording started. Bot will automatically stop when meeting ends...")
            print("Press Ctrl+C to stop manually")
            
            # Wait for meeting to end
            while self.meeting_active:
                time.sleep(5)
            
            # Stop recording
            audio_file = self.stop_audio_recording()
            
            if audio_file:
                print("🔄 Processing audio through pipeline...")
                results = self.process_audio_pipeline(audio_file)
                
                if results:
                    print("📧 Sending results to host...")
                    self.send_results_email(results, host_email)
                    print("✅ Process completed successfully!")
                else:
                    print("❌ Failed to process audio")
            else:
                print("❌ No audio was recorded")
                
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user")
        except Exception as e:
            print(f"❌ Error during meeting session: {str(e)}")
        finally:
            self.cleanup()
    
    def run_manual_mode(self, host_email=None):
        """
        Manual mode: User controls when to start/stop recording
        Good for testing without meeting integration
        """
        print("🤖 Done-Talking Bot - Manual Mode")
        print("This mode lets you control recording manually")
        
        try:
            input("Press Enter when you want to START recording...")
            self.start_audio_recording()
            
            print("📹 Recording... Press Enter when you want to STOP recording")
            input()
            
            audio_file = self.stop_audio_recording()
            
            if audio_file:
                print("🔄 Processing audio through pipeline...")
                results = self.process_audio_pipeline(audio_file)
                
                if results:
                    if host_email:
                        print("📧 Sending results to host...")
                        self.send_results_email(results, host_email)
                        print("✅ Process completed successfully!")
                    else:
                        print("✅ Processing completed!")
                        print(f"📁 Processed file: {results['processed_file']}")
                        print(f"📝 Summary: {results['summary']}")
                else:
                    print("❌ Failed to process audio")
            else:
                print("❌ No audio was recorded")
                
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped by user")
        except Exception as e:
            print(f"❌ Error during manual session: {str(e)}")
        finally:
            self.cleanup()

# Usage example
if __name__ == "__main__":
    print("🤖 Done-Talking Bot")
    print("=" * 40)
    
    # Initialize bot
    bot = DoneTalkingBot()
    
    print("\nChoose mode:")
    print("1. Manual recording mode (no Google Meet needed)")
    print("2. Auto meeting mode (requires Google Meet URL)")
    print("3. Test audio recording only")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        print("\n🔧 Manual Mode Selected")
        email = input("Enter email for results (or press Enter to skip): ").strip()
        if not email:
            email = None
        bot.run_manual_mode(email)
        
    elif choice == "2":
        print("\n🔧 Auto Mode Selected")
        meeting_url = input("Enter Google Meet URL: ").strip()
        host_email = input("Enter host email for results: ").strip()
        
        if not meeting_url or not host_email:
            print("❌ Both URL and email are required for auto mode")
        else:
            bot.run_meeting_session(meeting_url, host_email)
            
    elif choice == "3":
        print("\n🔧 Audio Test Mode")
        print("This will test audio recording for 10 seconds")
        input("Press Enter to start 10-second test recording...")
        
        bot.start_audio_recording()
        print("🎤 Recording... (10 seconds)")
        time.sleep(10)
        audio_file = bot.stop_audio_recording()
        
        if audio_file:
            print(f"✅ Test successful! Audio saved as: {audio_file}")
            
            # Test processing
            print("Testing audio processing...")
            results = bot.process_audio_pipeline(audio_file)
            if results:
                print("✅ Processing test successful!")
                print(f"📁 Processed file: {results['processed_file']}")
            else:
                print("❌ Processing test failed")
        else:
            print("❌ Test failed - no audio recorded")
            
    else:
        print("❌ Invalid choice")
    
    print("\n👋 Done-Talking Bot finished!")
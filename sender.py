#!/usr/bin/env python3
"""
IntraMirror OTP Sender - Termux Version (+255 Tanzania)
SECURED WITH NXTOOLS LICENSE SYSTEM
"""

import requests
import json
import re
import sys
import time
import os
import hashlib
import subprocess
import platform
from datetime import datetime

# ============================================
# LICENSE SYSTEM - NXTOOLS
# ============================================

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    @staticmethod
    def disable_colors():
        if not sys.stdout.isatty() or os.name == 'nt':
            for attr in ['GREEN', 'RED', 'YELLOW', 'BLUE', 'CYAN', 'MAGENTA', 'WHITE', 'RESET', 'BOLD', 'DIM']:
                setattr(Colors, attr, '')

class NXLicense:
    def __init__(self, tool_name="intramirror", secret_word="naha", 
                 pastebin_url="https://pastebin.com/raw/ez5BKAbT"):
        self.tool_name = tool_name
        self.secret_word = secret_word
        self.pastebin_url = pastebin_url
        self.license_file = os.path.expanduser(f"~/.{tool_name}_license.json")
        self.license_data = None
        self.load_license()
    
    def get_device_id(self):
        """Get unique device ID - PERMANENT for this device"""
        # Method 1: Android ID
        try:
            result = subprocess.run(
                ['content', 'query', '--uri', 'content://settings/secure', 
                 '--where', "name='android_id'"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                import re
                match = re.search(r'value=([a-f0-9]+)', result.stdout)
                if match:
                    android_id = match.group(1)
                    if android_id and len(android_id) > 5:
                        return f"ANDROID:{android_id}"
        except:
            pass
        
        # Method 2: Build fingerprint
        try:
            result = subprocess.run(
                ['getprop', 'ro.build.fingerprint'],
                capture_output=True, text=True, timeout=5
            )
            fingerprint = result.stdout.strip()
            if fingerprint and len(fingerprint) > 10:
                return f"FINGERPRINT:{hashlib.md5(fingerprint.encode()).hexdigest()[:16]}"
        except:
            pass
        
        # Method 3: Permanent fallback
        try:
            username = os.getenv('USER', 'user')
            hostname = platform.node()
            home = os.path.expanduser("~")
            unique = f"{username}|{home}|{hostname}"
            return f"DEVICE:{hashlib.md5(unique.encode()).hexdigest()[:16]}"
        except:
            return f"DEVICE:{hashlib.md5(str(os.getpid()).encode()).hexdigest()[:16]}"
    
    def get_device_model(self):
        """Get device model"""
        try:
            result = subprocess.run(
                ['getprop', 'ro.product.model'],
                capture_output=True, text=True, timeout=5
            )
            model = result.stdout.strip()
            if model:
                return model
        except:
            pass
        
        try:
            result = subprocess.run(
                ['getprop', 'ro.product.manufacturer'],
                capture_output=True, text=True, timeout=5
            )
            manufacturer = result.stdout.strip()
            result = subprocess.run(
                ['getprop', 'ro.product.model'],
                capture_output=True, text=True, timeout=5
            )
            model = result.stdout.strip()
            if manufacturer and model:
                return f"{manufacturer} {model}"
        except:
            pass
        
        return platform.node() or "Unknown_Device"
    
    def generate_key(self):
        """Generate PERMANENT license key from device info"""
        device_id = self.get_device_id()
        device_model = self.get_device_model()
        
        raw_data = f"{device_id}|{device_model}|{self.secret_word}|{self.tool_name}"
        hash_obj = hashlib.sha256(raw_data.encode())
        hash_hex = hash_obj.hexdigest()
        
        request_code = f"REQ-{hash_hex[:12].upper()}"
        
        return {
            "request_code": request_code,
            "device_id": device_id,
            "device_model": device_model
        }
    
    def check_pastebin(self, request_code):
        """Check if request code exists in Pastebin"""
        try:
            response = requests.get(self.pastebin_url, timeout=10)
            if response.status_code != 200:
                return None
            
            content = response.text.strip()
            if not content:
                return None
            
            for line in content.split('\n'):
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split('|')
                if len(parts) >= 5:
                    tool, req, app, expiry, user = parts[:5]
                    if req == request_code and tool == self.tool_name:
                        return {
                            "tool": tool,
                            "request_code": req,
                            "expiry_date": expiry,
                            "user_info": user
                        }
            return None
        except:
            return None
    
    def check(self):
        """Check license status - generates key and checks Pastebin"""
        key_info = self.generate_key()
        request_code = key_info["request_code"]
        
        # Check local cache first
        if self.license_data and self.license_data.get("status") == "active":
            if self.license_data.get("device_id") == key_info["device_id"]:
                expiry = self.license_data.get("expiry_date")
                if expiry:
                    try:
                        expiry_date = datetime.fromisoformat(expiry)
                        if datetime.now() > expiry_date:
                            return {
                                "status": "expired",
                                "message": f"License expired on {expiry}",
                                "request_code": request_code
                            }
                        remaining = (expiry_date - datetime.now()).days
                    except:
                        remaining = None
                else:
                    remaining = None
                
                return {
                    "status": "active",
                    "message": "License valid",
                    "request_code": request_code,
                    "user_info": self.license_data.get("user_info"),
                    "expiry_date": expiry,
                    "remaining_days": remaining
                }
        
        # Check Pastebin
        approval_data = self.check_pastebin(request_code)
        
        if not approval_data:
            return {
                "status": "denied",
                "message": "Not approved",
                "request_code": request_code
            }
        
        # Check expiry
        expiry_date = approval_data.get("expiry_date")
        if expiry_date:
            try:
                expiry = datetime.fromisoformat(expiry_date)
                if datetime.now() > expiry:
                    return {
                        "status": "expired",
                        "message": f"License expired on {expiry_date}",
                        "request_code": request_code,
                        "expiry_date": expiry_date
                    }
                remaining = (expiry - datetime.now()).days
            except:
                remaining = None
        else:
            remaining = None
        
        # ✅ Approved! Save license locally
        license_data = {
            "tool_name": self.tool_name,
            "request_code": request_code,
            "device_id": key_info["device_id"],
            "device_model": key_info["device_model"],
            "user_info": approval_data.get("user_info"),
            "expiry_date": expiry_date,
            "activated_date": datetime.now().isoformat(),
            "status": "active"
        }
        self.save_license(license_data)
        
        return {
            "status": "active",
            "message": "✅ License approved!",
            "request_code": request_code,
            "user_info": approval_data.get("user_info"),
            "expiry_date": expiry_date,
            "remaining_days": remaining
        }
    
    def save_license(self, license_data):
        """Save license locally"""
        try:
            with open(self.license_file, 'w') as f:
                json.dump(license_data, f, indent=2)
        except:
            pass
    
    def load_license(self):
        """Load existing license"""
        if os.path.exists(self.license_file):
            try:
                with open(self.license_file, 'r') as f:
                    self.license_data = json.load(f)
                return self.license_data
            except:
                self.license_data = None
                return None
        self.license_data = None
        return None
    
    def require(self):
        """Main function - check license and show status"""
        result = self.check()
        
        print("\n" + "="*60)
        print(f"{Colors.CYAN}{Colors.BOLD}  🔐 {self.tool_name.upper()} License{Colors.RESET}")
        print("="*60)
        
        if result["status"] == "active":
            print(f"{Colors.GREEN}✅ {result['message']}{Colors.RESET}")
            if result.get("user_info"):
                print(f"  {Colors.DIM}User:{Colors.RESET}     {result['user_info']}")
            if result.get("remaining_days") is not None:
                print(f"  {Colors.DIM}Remaining:{Colors.RESET} {result['remaining_days']} days")
            if result.get("expiry_date"):
                print(f"  {Colors.DIM}Expires:{Colors.RESET}  {result['expiry_date']}")
            print("="*60)
            print(f"{Colors.GREEN}🎉 Access Granted!{Colors.RESET}")
            return True
            
        elif result["status"] == "expired":
            print(f"{Colors.RED}❌ {result['message']}{Colors.RESET}")
            print("="*60)
            print(f"{Colors.YELLOW}💡 Contact admin for extension{Colors.RESET}")
            return False
            
        elif result["status"] == "denied":
            print(f"{Colors.RED}❌ {result['message']}{Colors.RESET}")
            print(f"\n{Colors.YELLOW}📤 Send this request code to admin:{Colors.RESET}")
            print(f"  {Colors.BOLD}{Colors.CYAN}{result['request_code']}{Colors.RESET}")
            print(f"\n{Colors.DIM}Admin will add this code to Pastebin{Colors.RESET}")
            print("="*60)
            return False
            
        else:
            print(f"{Colors.RED}❌ Unknown error{Colors.RESET}")
            return False

# ============================================
# DEBUG MODE - Set to True to see detailed logs
# ============================================
DEBUG = False
# ============================================

# ============================================
# PROXY CONFIGURATION
# ============================================
PROXY = "942fd9a198553847cf8a__cr.tz:1f54ed1d3311298f@gw.dataimpulse.com:823"
USE_PROXY = True  # Set to False to disable proxy
# ============================================

class IntraMirrorSignupBot:
    def __init__(self, delay=0.5):
        self.base_url = "https://imgateway.intramirror.com"
        self.web_url = "https://imapp.intramirror.com"
        self.delay = delay
        
        self.total = 0
        self.success = 0
        self.failed = 0
        
        # Setup proxy
        self.proxy = None
        if USE_PROXY and PROXY:
            try:
                proxy_parts = PROXY.split('@')
                if len(proxy_parts) == 2:
                    auth_part = proxy_parts[0]
                    server_part = proxy_parts[1]
                    
                    if ':' in auth_part and '__cr.mm' in auth_part:
                        if ':' in server_part:
                            host, port = server_part.split(':')
                            if '__cr.mm' in auth_part:
                                username_parts = auth_part.split(':')
                                if len(username_parts) >= 2:
                                    username = username_parts[0]
                                    password = ':'.join(username_parts[1:])
                                    
                                    proxy_auth = f"{username}:{password}"
                                    self.proxy = {
                                        'http': f'http://{proxy_auth}@{host}:{port}',
                                        'https': f'https://{proxy_auth}@{host}:{port}'
                                    }
                    
                    if not self.proxy:
                        if ':' in auth_part and ':' in server_part:
                            host, port = server_part.split(':')
                            username, password = auth_part.split(':', 1)
                            self.proxy = {
                                'http': f'http://{username}:{password}@{host}:{port}',
                                'https': f'https://{username}:{password}@{host}:{port}'
                            }
                
                if self.proxy and DEBUG:
                    print(f"{Colors.GREEN}✅ Proxy configured: {self.proxy['http']}{Colors.RESET}")
            except Exception as e:
                if DEBUG:
                    print(f"{Colors.RED}❌ Failed to parse proxy: {e}{Colors.RESET}")
                self.proxy = None
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Mobile Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Origin': self.web_url,
            'Referer': f'{self.web_url}/im-invite-signup-official/signup.html?invitationChannelId=31',
            'Content-Type': 'application/json;charset=UTF-8',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site'
        }
    
    def debug_print(self, title, data, color=Colors.MAGENTA):
        """Print debug information if DEBUG is True"""
        if DEBUG:
            print(f"\n{color}{Colors.BOLD}┌─ {title}{Colors.RESET}")
            print(f"{color}│{Colors.RESET}")
            if isinstance(data, dict):
                for key, value in data.items():
                    print(f"{color}│ {Colors.WHITE}{key}:{Colors.RESET} {json.dumps(value, indent=2) if isinstance(value, (dict, list)) else value}")
            elif isinstance(data, str):
                print(f"{color}│ {Colors.WHITE}{data}{Colors.RESET}")
            else:
                print(f"{color}│ {Colors.WHITE}{json.dumps(data, indent=2)}{Colors.RESET}")
            print(f"{color}└─────────────────────────────────{Colors.RESET}\n")
    
    def send_otp(self, country_code, phone_number):
        phone_number = re.sub(r'\D', '', phone_number)
        
        if not phone_number or len(phone_number) < 5:
            return {'status': 0, 'msg': 'Invalid', 'display': f"+{country_code} {phone_number}"}
        
        session = requests.Session()
        session.headers.update(self.headers)
        
        if self.proxy:
            session.proxies.update(self.proxy)
            if DEBUG:
                print(f"{Colors.DIM}🔗 Using proxy: {self.proxy['http']}{Colors.RESET}")
        
        payload = {
            'countryCode': str(country_code),
            'mobile': phone_number,
            'type': 10
        }
        
        url = f"{self.base_url}/imapp/new/alisms/send/check/code"
        
        if DEBUG:
            print(f"\n{Colors.CYAN}{Colors.BOLD}📤 REQUEST{Colors.RESET}")
            print(f"{Colors.DIM}URL: {url}{Colors.RESET}")
            print(f"{Colors.DIM}Method: POST{Colors.RESET}")
            if self.proxy:
                print(f"{Colors.DIM}Proxy: {self.proxy['http']}{Colors.RESET}")
            self.debug_print("Headers", self.headers, Colors.BLUE)
            self.debug_print("Payload", payload, Colors.YELLOW)
        
        try:
            response = session.post(url, json=payload, timeout=15)
            
            if DEBUG:
                print(f"\n{Colors.MAGENTA}{Colors.BOLD}📥 RESPONSE{Colors.RESET}")
                print(f"{Colors.DIM}Status Code: {response.status_code}{Colors.RESET}")
                print(f"{Colors.DIM}Headers:{Colors.RESET}")
                for key, value in response.headers.items():
                    print(f"  {Colors.DIM}{key}:{Colors.RESET} {value}")
                
                try:
                    response_json = response.json()
                    self.debug_print("Response Body", response_json, Colors.GREEN)
                except:
                    self.debug_print("Response Body (Raw)", response.text, Colors.GREEN)
            
            response.raise_for_status()
            result = response.json()
            
            return {
                'status': result.get('status', 0),
                'msg': result.get('msg', ''),
                'display': f"+{country_code} {phone_number}",
                'phone': phone_number
            }
        except requests.exceptions.ProxyError as e:
            if DEBUG:
                print(f"\n{Colors.RED}{Colors.BOLD}❌ PROXY ERROR{Colors.RESET}")
                print(f"{Colors.RED}Failed to connect through proxy: {str(e)}{Colors.RESET}")
            return {'status': 0, 'msg': f'Proxy error: {str(e)[:50]}', 'display': f"+{country_code} {phone_number}", 'phone': phone_number}
        except requests.exceptions.RequestException as e:
            if DEBUG:
                print(f"\n{Colors.RED}{Colors.BOLD}❌ ERROR{Colors.RESET}")
                print(f"{Colors.RED}Exception: {str(e)}{Colors.RESET}")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"{Colors.RED}Response Status: {e.response.status_code}{Colors.RESET}")
                    try:
                        print(f"{Colors.RED}Response Body: {e.response.text}{Colors.RESET}")
                    except:
                        pass
            return {'status': 0, 'msg': str(e), 'display': f"+{country_code} {phone_number}", 'phone': phone_number}
        except json.JSONDecodeError as e:
            if DEBUG:
                print(f"\n{Colors.RED}{Colors.BOLD}❌ JSON ERROR{Colors.RESET}")
                print(f"{Colors.RED}Exception: {str(e)}{Colors.RESET}")
                print(f"{Colors.RED}Raw Response: {response.text[:500]}{Colors.RESET}")
            return {'status': 0, 'msg': 'Invalid JSON response', 'display': f"+{country_code} {phone_number}", 'phone': phone_number}
        finally:
            session.close()
    
    def remove_number_from_file(self, phone, filename="number.txt"):
        try:
            if not os.path.exists(filename):
                return
            
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            phone_pattern = re.compile(rf'{re.escape(phone)}')
            new_lines = [line for line in lines if not phone_pattern.search(line)]
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
                
            if DEBUG:
                print(f"{Colors.DIM}📝 Removed {phone} from {filename}{Colors.RESET}")
        except Exception as e:
            if DEBUG:
                print(f"{Colors.RED}Failed to remove from file: {e}{Colors.RESET}")
            pass
    
    def process_numbers(self, numbers, filename="number.txt"):
        total = len(numbers)
        
        print(f"\n{Colors.CYAN}⚡ Processing {total} numbers")
        print(f"⏱️  Delay: {self.delay}s between each request")
        if DEBUG:
            print(f"{Colors.YELLOW}🐛 DEBUG MODE ENABLED - Showing all details{Colors.RESET}")
        if self.proxy:
            print(f"{Colors.GREEN}🔗 Proxy enabled: {self.proxy['http']}{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}🔗 Proxy disabled - Direct connection{Colors.RESET}")
        print(f"{Colors.RESET}\n")
        
        for idx, (country_code, phone) in enumerate(numbers, 1):
            result = self.send_otp(country_code, phone)
            
            self.total += 1
            if result['status'] == 1:
                self.success += 1
                print(f"{Colors.GREEN}✓ [{idx}/{total}] {result['display']} - SUCCESS{Colors.RESET}")
                self.remove_number_from_file(phone, filename)
            else:
                self.failed += 1
                error_msg = result.get('msg', 'Unknown error')[:50]
                print(f"{Colors.RED}✗ [{idx}/{total}] {result['display']} - {error_msg}{Colors.RESET}")
            
            if idx < total:
                if DEBUG:
                    print(f"{Colors.DIM}⏳ Waiting {self.delay}s before next request...{Colors.RESET}")
                time.sleep(self.delay)
    
    def print_stats(self):
        print("\n" + "="*60)
        print(f"{Colors.CYAN}{Colors.BOLD}📊 STATISTICS{Colors.RESET}")
        print("="*60)
        print(f"Total: {self.total}")
        print(f"{Colors.GREEN}Success: {self.success}{Colors.RESET}")
        print(f"{Colors.RED}Failed: {self.failed}{Colors.RESET}")
        if self.total > 0:
            print(f"Rate: {(self.success/self.total*100):.1f}%")
        print("="*60)

def get_file_path():
    """Get file path from user with Termux Android storage support"""
    print("\n" + "="*60)
    print(f"{Colors.CYAN}{Colors.BOLD}  📂 File Path Helper{Colors.RESET}")
    print("="*60)
    
    print(f"\n{Colors.CYAN}📝 Enter the path to your number.txt file{Colors.RESET}")
    print(f"{Colors.DIM}💡 Example: /sdcard/Download/number.txt{Colors.RESET}")
    print(f"{Colors.DIM}💡 Or just press Enter for default: number.txt in current directory{Colors.RESET}")
    
    while True:
        file_path = input(f"\n{Colors.YELLOW}📁 Path [default: number.txt]: {Colors.RESET}").strip()
        
        if not file_path:
            file_path = "number.txt"
        
        file_path = os.path.expanduser(file_path)
        
        if os.path.exists(file_path):
            if os.path.isfile(file_path):
                print(f"{Colors.GREEN}✅ File found: {file_path}{Colors.RESET}")
                return file_path
            else:
                print(f"{Colors.RED}❌ Path exists but is not a file{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ File not found: {file_path}{Colors.RESET}")
            retry = input(f"{Colors.YELLOW}Try again? (y/n): {Colors.RESET}").lower()
            if retry != 'y':
                return None

def read_numbers(filename="number.txt"):
    numbers = []
    default_country = "255"
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                if ':' in line:
                    parts = line.split(':', 1)
                    country_code = parts[0].strip()
                    phone = parts[1].strip()
                else:
                    country_code = default_country
                    phone = line
                
                phone = re.sub(r'\D', '', phone)
                
                if phone and len(phone) >= 5:
                    numbers.append((country_code, phone))
    except FileNotFoundError:
        print(f"{Colors.RED}❌ {filename} not found{Colors.RESET}")
        return []
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")
        return []
    
    return numbers

def check_termux_storage():
    """Check and setup Termux storage if needed"""
    try:
        storage_path = os.path.expanduser("~/storage")
        if not os.path.exists(storage_path):
            print(f"{Colors.YELLOW}⚠️ Termux storage not set up{Colors.RESET}")
            print(f"{Colors.CYAN}💡 Run this command to set up storage:{Colors.RESET}")
            print(f"  {Colors.DIM}termux-setup-storage{Colors.RESET}")
            print(f"{Colors.YELLOW}Then restart this script{Colors.RESET}")
            return False
        return True
    except:
        return False

def main():
    # 🚀 FIRST: Check License
    print(f"\n{Colors.CYAN}🔐 Checking license...{Colors.RESET}")
    license_check = NXLicense(tool_name="intramirror")
    
    if not license_check.require():
        print(f"\n{Colors.RED}❌ License check failed. Tool cannot run.{Colors.RESET}")
        sys.exit(1)
    
    # ✅ License approved - proceed with main program
    print(f"\n{Colors.GREEN}✅ License verified. Starting tool...{Colors.RESET}\n")
    
    # Check Termux environment
    is_termux = os.path.exists("/data/data/com.termux")
    
    if is_termux:
        print(f"{Colors.GREEN}🔍 Termux environment detected{Colors.RESET}")
        check_termux_storage()
    
    print("\n" + "="*60)
    print(f"{Colors.CYAN}{Colors.BOLD}  IntraMirror OTP Sender - Termux (+255 Tanzania){Colors.RESET}")
    print("="*60)
    if DEBUG:
        print(f"{Colors.YELLOW}🐛 DEBUG MODE: ON{Colors.RESET}")
    else:
        print(f"{Colors.DIM}🔇 DEBUG MODE: OFF (Set DEBUG=True for details){Colors.RESET}")
    if USE_PROXY and PROXY:
        print(f"{Colors.GREEN}🔗 PROXY: ENABLED{Colors.RESET}")
        print(f"{Colors.DIM}   Proxy: {PROXY}{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}🔗 PROXY: DISABLED{Colors.RESET}")
    print(f"{Colors.CYAN}📱 Default Country Code: +255 (Tanzania){Colors.RESET}")
    print("="*60 + "\n")
    
    filename = get_file_path()
    if not filename:
        print(f"{Colors.RED}❌ No file selected. Exiting.{Colors.RESET}")
        return
    
    numbers = read_numbers(filename)
    
    if not numbers:
        print(f"{Colors.RED}❌ No valid numbers found{Colors.RESET}")
        print(f"{Colors.YELLOW}Format: country_code:phone_number (e.g., 255:1234567890){Colors.RESET}")
        print(f"{Colors.YELLOW}Or just phone number (will use +255 by default){Colors.RESET}")
        return
    
    print(f"{Colors.BLUE}📋 Found {len(numbers)} number(s){Colors.RESET}")
    
    print(f"\n{Colors.YELLOW}Configure Delay:{Colors.RESET}")
    
    while True:
        try:
            delay = float(input(f"Delay between requests in seconds (0.01-5) [default: 0.5]: ").strip() or "0.5")
            if 0.01 <= delay <= 5:
                break
            print(f"{Colors.RED}Please enter between 0.01-5{Colors.RESET}")
        except:
            delay = 0.5
            break
    
    print(f"\n{Colors.CYAN}⏱️  Using {delay}s delay between requests{Colors.RESET}")
    
    print(f"\n{Colors.BLUE}Numbers to process:{Colors.RESET}")
    for idx, (country, phone) in enumerate(numbers[:10], 1):
        print(f"  {idx}. +{country} {phone}")
    if len(numbers) > 10:
        print(f"  ... and {len(numbers)-10} more")
    
    print(f"\n{Colors.YELLOW}Starting in 3 seconds... Press Ctrl+C to cancel{Colors.RESET}")
    for i in range(3, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    
    print(f"\n{Colors.GREEN}▶️ Starting OTP sending...{Colors.RESET}")
    
    start = time.time()
    bot = IntraMirrorSignupBot(delay=delay)
    bot.process_numbers(numbers, filename)
    
    elapsed = time.time() - start
    
    bot.print_stats()
    if bot.total > 0:
        print(f"\n{Colors.CYAN}⏱️  Time: {elapsed:.2f}s{Colors.RESET}")
        print(f"{Colors.CYAN}📊 Speed: {(bot.total/elapsed):.2f} OTPs/sec{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️ Interrupted by user{Colors.RESET}")
        sys.exit(0)

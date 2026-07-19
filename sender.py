#!/usr/bin/env python3
"""
IntraMirror OTP Sender - Termux Version (+255 Tanzania)
"""

import requests
import json
import re
import sys
import time
import os

# ============================================
# DEBUG MODE - Set to True to see detailed logs
# ============================================
DEBUG = False
# ============================================

# ============================================
# PROXY CONFIGURATION
# ============================================
PROXY = "942fd9a198553847cf8a__cr.mm:1f54ed1d3311298f@gw.dataimpulse.com:823"
USE_PROXY = True  # Set to False to disable proxy
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

Colors.disable_colors()

class IntraMirrorSignupBot:
    def __init__(self, delay=0.5):
        self.base_url = "https://imgateway.intramirror.com"
        self.web_url = "https://imapp.intramirror.com"
        self.delay = delay
        
        self.total = 0
        self.success = 0
        self.failed = 0
        
        # Setup proxy - EXACTLY like the PC version
        self.proxy = None
        if USE_PROXY and PROXY:
            try:
                # Parse proxy string
                proxy_parts = PROXY.split('@')
                if len(proxy_parts) == 2:
                    auth_part = proxy_parts[0]
                    server_part = proxy_parts[1]
                    
                    # Handle different proxy formats
                    if ':' in auth_part and '__cr.mm' in auth_part:
                        # Format: username:password@host:port
                        # Special format: username__cr.mm:password@host:port
                        if ':' in server_part:
                            host, port = server_part.split(':')
                            # Find the actual username and password
                            # The username is everything before the first colon in auth_part
                            # but we need to handle the special __cr.mm format
                            if '__cr.mm' in auth_part:
                                # Special format: username__cr.mm:password
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
                        # Try simple format: username:password@host:port
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
        
        # Set proxy if configured
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
        
        # Debug: Show request details
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
            
            # Debug: Show response details
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
            # Send OTP
            result = self.send_otp(country_code, phone)
            
            # Update stats
            self.total += 1
            if result['status'] == 1:
                self.success += 1
                print(f"{Colors.GREEN}✓ [{idx}/{total}] {result['display']} - SUCCESS{Colors.RESET}")
                self.remove_number_from_file(phone, filename)
            else:
                self.failed += 1
                error_msg = result.get('msg', 'Unknown error')[:50]
                print(f"{Colors.RED}✗ [{idx}/{total}] {result['display']} - {error_msg}{Colors.RESET}")
            
            # Wait before next request (except after last)
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
    
    # Ask for file path
    print(f"\n{Colors.CYAN}📝 Enter the path to your number.txt file{Colors.RESET}")
    print(f"{Colors.DIM}💡 Example: /sdcard/Download/number.txt{Colors.RESET}")
    print(f"{Colors.DIM}💡 Or just press Enter for default: number.txt in current directory{Colors.RESET}")
    
    while True:
        file_path = input(f"\n{Colors.YELLOW}📁 Path [default: number.txt]: {Colors.RESET}").strip()
        
        # Use default if empty
        if not file_path:
            file_path = "number.txt"
        
        # Expand user path (~)
        file_path = os.path.expanduser(file_path)
        
        # Check if file exists
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
    default_country = "255"  # Tanzania
    
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
    # Check Termux environment
    is_termux = os.path.exists("/data/data/com.termux")
    
    if is_termux:
        print(f"\n{Colors.GREEN}🔍 Termux environment detected{Colors.RESET}")
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
    
    # Get file path from user
    filename = get_file_path()
    if not filename:
        print(f"{Colors.RED}❌ No file selected. Exiting.{Colors.RESET}")
        return
    
    # Read numbers - EXACTLY like the PC version
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

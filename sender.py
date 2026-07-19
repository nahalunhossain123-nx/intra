#!/usr/bin/env python3
"""
IntraMirror OTP Sender - Termux Version
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
PROXY = "942fd9a198553847cf8a__cr.eg:1f54ed1d3311298f@gw.dataimpulse.com:823"
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
        
        # Setup proxy
        self.proxy = None
        if USE_PROXY and PROXY:
            try:
                proxy_parts = PROXY.split('@')
                if len(proxy_parts) == 2:
                    auth_part = proxy_parts[0]
                    server_part = proxy_parts[1]
                    
                    if ':' in auth_part and '__cr.eg' in auth_part:
                        if ':' in server_part:
                            host, port = server_part.split(':')
                            if '__cr.eg' in auth_part:
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
    
    def remove_number_from_file(self, phone, filename):
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
    
    def process_numbers(self, numbers, filename):
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
    print(f"{Colors.CYAN}{Colors.BOLD}  📂 Termux File Path Helper{Colors.RESET}")
    print("="*60)
    
    # Common Termux storage paths
    common_paths = [
        ("Internal Storage Download", "/sdcard/Download/number.txt"),
        ("Internal Storage Download (alt)", "/storage/emulated/0/Download/number.txt"),
        ("Termux Home", "~/number.txt"),
        ("Termux Storage Download", "~/storage/downloads/number.txt"),
        ("Custom Path", "custom")
    ]
    
    print(f"\n{Colors.YELLOW}Common storage paths:{Colors.RESET}")
    for i, (name, path) in enumerate(common_paths, 1):
        if path != "custom":
            expanded = os.path.expanduser(path)
            exists = "✅" if os.path.exists(expanded) else "❌"
            print(f"  {Colors.BLUE}{i}.{Colors.RESET} {name}: {Colors.DIM}{path}{Colors.RESET} {exists}")
        else:
            print(f"  {Colors.BLUE}{i}.{Colors.RESET} {name}")
    
    print(f"\n{Colors.CYAN}📝 Enter the path to your number.txt file{Colors.RESET}")
    print(f"{Colors.DIM}💡 Example: /sdcard/Download/number.txt{Colors.RESET}")
    
    while True:
        file_path = input(f"\n{Colors.YELLOW}📁 Path: {Colors.RESET}").strip()
        
        # Handle shortcut input (just the number)
        if file_path.isdigit():
            idx = int(file_path) - 1
            if 0 <= idx < len(common_paths):
                path = common_paths[idx][1]
                if path == "custom":
                    file_path = input(f"{Colors.YELLOW}📁 Enter custom path: {Colors.RESET}").strip()
                else:
                    file_path = path
        
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

def read_numbers(filename):
    """Read numbers from file with flexible format"""
    numbers = []
    default_country = "20"  # Egypt default
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"\n{Colors.DIM}📄 File content preview:{Colors.RESET}")
            lines_preview = content.split('\n')[:5]
            for line in lines_preview:
                if line.strip():
                    print(f"  {Colors.DIM}{line.strip()}{Colors.RESET}")
            if len(content.split('\n')) > 5:
                print(f"  {Colors.DIM}... and more lines{Colors.RESET}")
            
            f.seek(0)
            
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Check format: with or without country code
                if ':' in line:
                    parts = line.split(':', 1)
                    country_code = parts[0].strip()
                    phone = parts[1].strip()
                else:
                    # If no country code, ask user
                    print(f"\n{Colors.YELLOW}⚠️ No country code found for: {line}{Colors.RESET}")
                    use_default = input(f"Use default country code ({default_country})? (y/n): ").lower()
                    if use_default == 'y':
                        country_code = default_country
                        phone = line
                    else:
                        country_code = input(f"Enter country code for {line}: ").strip()
                        phone = line
                
                # Clean phone number
                phone = re.sub(r'\D', '', phone)
                
                if phone and len(phone) >= 5:
                    numbers.append((country_code, phone))
                else:
                    print(f"{Colors.RED}⚠️ Line {line_num}: Invalid phone number (min 5 digits){Colors.RESET}")
                    
    except FileNotFoundError:
        print(f"{Colors.RED}❌ File not found: {filename}{Colors.RESET}")
        return []
    except PermissionError:
        print(f"{Colors.RED}❌ Permission denied: {filename}{Colors.RESET}")
        print(f"{Colors.YELLOW}💡 In Termux, make sure you have storage permissions:{Colors.RESET}")
        print(f"  {Colors.DIM}termux-setup-storage{Colors.RESET}")
        return []
    except Exception as e:
        print(f"{Colors.RED}❌ Error reading file: {e}{Colors.RESET}")
        return []
    
    return numbers

def check_termux_storage():
    """Check and setup Termux storage if needed"""
    try:
        # Check if storage directory exists
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
    print(f"{Colors.CYAN}{Colors.BOLD}  IntraMirror OTP Sender - Termux{Colors.RESET}")
    print("="*60)
    
    if DEBUG:
        print(f"{Colors.YELLOW}🐛 DEBUG MODE: ON{Colors.RESET}")
    else:
        print(f"{Colors.DIM}🔇 DEBUG MODE: OFF (Set DEBUG=True for details){Colors.RESET}")
    
    if USE_PROXY and PROXY:
        print(f"{Colors.GREEN}🔗 PROXY: ENABLED{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}🔗 PROXY: DISABLED{Colors.RESET}")
    print("="*60 + "\n")
    
    # Get file path from user
    filename = get_file_path()
    if not filename:
        print(f"{Colors.RED}❌ No file selected. Exiting.{Colors.RESET}")
        return
    
    # Read numbers
    numbers = read_numbers(filename)
    
    if not numbers:
        print(f"{Colors.RED}❌ No valid numbers found in file{Colors.RESET}")
        print(f"{Colors.YELLOW}Format: country_code:phone_number (e.g., 20:1234567890){Colors.RESET}")
        return
    
    print(f"\n{Colors.BLUE}📋 Found {len(numbers)} number(s){Colors.RESET}")
    
    # Show first few numbers
    print(f"\n{Colors.DIM}First 5 numbers:{Colors.RESET}")
    for idx, (country, phone) in enumerate(numbers[:5], 1):
        print(f"  {idx}. +{country} {phone}")
    if len(numbers) > 5:
        print(f"  {Colors.DIM}... and {len(numbers)-5} more{Colors.RESET}")
    
    # Get delay
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
    
    # Confirmation
    print(f"\n{Colors.YELLOW}⚠️ Ready to send OTPs to {len(numbers)} numbers{Colors.RESET}")
    confirm = input(f"Continue? (y/n): ").lower()
    if confirm != 'y':
        print(f"{Colors.YELLOW}Cancelled{Colors.RESET}")
        return
    
    print(f"\n{Colors.GREEN}▶️ Starting OTP sending...{Colors.RESET}")
    
    # Process
    start = time.time()
    bot = IntraMirrorSignupBot(delay=delay)
    bot.process_numbers(numbers, filename)
    
    elapsed = time.time() - start
    
    # Show results
    bot.print_stats()
    if bot.total > 0:
        print(f"\n{Colors.CYAN}⏱️  Time: {elapsed:.2f}s{Colors.RESET}")
        print(f"{Colors.CYAN}📊 Speed: {(bot.total/elapsed):.2f} OTPs/sec{Colors.RESET}")
    
    print(f"\n{Colors.GREEN}✅ Done!{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️ Interrupted by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.RESET}")
        sys.exit(1)

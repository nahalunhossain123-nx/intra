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
# LICENSE SYSTEM - NXTOOLS (DEBUG VERSION)
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
        self.debug = True  # Enable debug for license checking
    
    def debug_print(self, title, data):
        """Print debug info"""
        if self.debug:
            print(f"\n{Colors.CYAN}🔍 {title}{Colors.RESET}")
            print(f"{Colors.DIM}{data}{Colors.RESET}")
    
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
                        device_id = f"ANDROID:{android_id}"
                        self.debug_print("Device ID", f"Using Android ID: {device_id}")
                        return device_id
        except Exception as e:
            self.debug_print("Android ID error", str(e))
        
        # Method 2: Build fingerprint
        try:
            result = subprocess.run(
                ['getprop', 'ro.build.fingerprint'],
                capture_output=True, text=True, timeout=5
            )
            fingerprint = result.stdout.strip()
            if fingerprint and len(fingerprint) > 10:
                device_id = f"FINGERPRINT:{hashlib.md5(fingerprint.encode()).hexdigest()[:16]}"
                self.debug_print("Device ID", f"Using Fingerprint: {device_id}")
                return device_id
        except Exception as e:
            self.debug_print("Fingerprint error", str(e))
        
        # Method 3: Permanent fallback
        try:
            username = os.getenv('USER', 'user')
            hostname = platform.node()
            home = os.path.expanduser("~")
            unique = f"{username}|{home}|{hostname}"
            device_id = f"DEVICE:{hashlib.md5(unique.encode()).hexdigest()[:16]}"
            self.debug_print("Device ID", f"Using Fallback: {device_id}")
            return device_id
        except Exception as e:
            device_id = f"DEVICE:{hashlib.md5(str(os.getpid()).encode()).hexdigest()[:16]}"
            self.debug_print("Device ID", f"Using PID Fallback: {device_id}")
            return device_id
    
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
        self.debug_print("Raw Data for Hash", raw_data)
        
        hash_obj = hashlib.sha256(raw_data.encode())
        hash_hex = hash_obj.hexdigest()
        self.debug_print("Hash", hash_hex)
        
        request_code = f"REQ-{hash_hex[:12].upper()}"
        self.debug_print("Generated Request Code", request_code)
        
        return {
            "request_code": request_code,
            "device_id": device_id,
            "device_model": device_model
        }
    
    def check_pastebin(self, request_code):
        """Check if request code exists in Pastebin"""
        print(f"\n{Colors.YELLOW}📡 Checking Pastebin for license...{Colors.RESET}")
        print(f"{Colors.DIM}URL: {self.pastebin_url}{Colors.RESET}")
        print(f"{Colors.DIM}Looking for code: {request_code}{Colors.RESET}")
        
        try:
            response = requests.get(self.pastebin_url, timeout=10)
            print(f"{Colors.DIM}Response Status: {response.status_code}{Colors.RESET}")
            
            if response.status_code != 200:
                print(f"{Colors.RED}❌ Failed to fetch Pastebin (Status: {response.status_code}){Colors.RESET}")
                return None
            
            content = response.text.strip()
            print(f"{Colors.DIM}Pastebin Content:{Colors.RESET}")
            print(f"{Colors.DIM}{'-'*40}{Colors.RESET}")
            print(content)
            print(f"{Colors.DIM}{'-'*40}{Colors.RESET}")
            
            if not content:
                print(f"{Colors.RED}❌ Pastebin is empty{Colors.RESET}")
                return None
            
            # Try to find matching line
            for line_num, line in enumerate(content.split('\n'), 1):
                line = line.strip()
                if not line:
                    continue
                
                print(f"{Colors.DIM}Checking line {line_num}: {line}{Colors.RESET}")
                
                parts = line.split('|')
                if len(parts) >= 5:
                    tool, req, app, expiry, user = parts[:5]
                    print(f"{Colors.DIM}  Tool: {tool}, Request: {req}{Colors.RESET}")
                    
                    if req == request_code and tool == self.tool_name:
                        print(f"{Colors.GREEN}✅ Found matching license!{Colors.RESET}")
                        return {
                            "tool": tool,
                            "request_code": req,
                            "expiry_date": expiry,
                            "user_info": user
                        }
                else:
                    print(f"{Colors.YELLOW}⚠️ Line {line_num} has {len(parts)} parts, expected at least 5{Colors.RESET}")
            
            print(f"{Colors.RED}❌ No matching license found in Pastebin{Colors.RESET}")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"{Colors.RED}❌ Network error: {e}{Colors.RESET}")
            return None
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")
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
                    "message": "License valid (cached)",
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
                "message": "Not approved - Check Pastebin content above",
                "request_code": request_code
            }
        
        # Check expiry
        expiry_date = approval_data.get("expiry_date")
        if expiry_date and expiry_date != "none" and expiry_date != "never":
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
            except Exception as e:
                print(f"{Colors.YELLOW}⚠️ Could not parse expiry date: {e}{Colors.RESET}")
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
            print(f"{Colors.GREEN}✅ License saved to {self.license_file}{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}❌ Could not save license: {e}{Colors.RESET}")
    
    def load_license(self):
        """Load existing license"""
        if os.path.exists(self.license_file):
            try:
                with open(self.license_file, 'r') as f:
                    self.license_data = json.load(f)
                print(f"{Colors.GREEN}✅ Loaded cached license from {self.license_file}{Colors.RESET}")
                return self.license_data
            except Exception as e:
                print(f"{Colors.YELLOW}⚠️ Could not load license: {e}{Colors.RESET}")
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
            print(f"\n{Colors.DIM}Admin must add this EXACT code to Pastebin{Colors.RESET}")
            print(f"{Colors.DIM}Format: {self.tool_name}|{result['request_code']}|approved|2026-12-31|username{Colors.RESET}")
            print(f"{Colors.DIM}Example: {self.tool_name}|{result['request_code']}|approved|2026-12-31|your_username{Colors.RESET}")
            print("="*60)
            return False
            
        else:
            print(f"{Colors.RED}❌ Unknown error{Colors.RESET}")
            return False

# ============================================
# REST OF THE INTRA MIRROR CODE...
# ============================================

# [Keep all your existing IntraMirrorSignupBot class and functions here]
# I'm showing only the license part for brevity, but include everything else

# ============================================

def main():
    # 🚀 FIRST: Check License
    print(f"\n{Colors.CYAN}🔐 Checking license...{Colors.RESET}")
    license_check = NXLicense(tool_name="intramirror")
    
    if not license_check.require():
        print(f"\n{Colors.RED}❌ License check failed. Tool cannot run.{Colors.RESET}")
        sys.exit(1)
    
    # ✅ License approved - proceed with main program
    print(f"\n{Colors.GREEN}✅ License verified. Starting tool...{Colors.RESET}\n")
    
    # [Rest of your main function...]

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️ Interrupted by user{Colors.RESET}")
        sys.exit(0)

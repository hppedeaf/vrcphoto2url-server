#!/usr/bin/env python3
"""
VRCPhoto2URL Connection & Upload Verification Test
Comprehensive test to verify all functionality is working after the API key fix
"""

import json
import requests
import time
from datetime import datetime
from pathlib import Path

class VRCPhoto2URLVerification:
    def __init__(self):
        self.base_url = "https://vrcphoto2url-server-production.up.railway.app"
        self.api_key = "pjfR_FzOiqgmFOxxW9cfomsw7kOrDhgMv60vtBcG_GI"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.test_results = []
        
    def print_header(self, text):
        print(f"\n{'='*60}")
        print(f"🧪 {text}")
        print(f"{'='*60}")
        
    def print_test(self, test_name, status, details=""):
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"{status_icon} {test_name:<30} {status}")
        if details:
            print(f"   📝 {details}")
        self.test_results.append({"test": test_name, "status": status, "details": details})
        
    def test_server_health(self):
        """Test server health endpoint"""
        self.print_header("SERVER HEALTH CHECK")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.print_test("Server Health", "PASS", f"Status: {data.get('status', 'unknown')}")
                return True
            else:
                self.print_test("Server Health", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_test("Server Health", "FAIL", f"Connection error: {str(e)}")
            return False
            
    def test_api_authentication(self):
        """Test API authentication with correct key"""
        self.print_header("API AUTHENTICATION")
        
        try:
            response = requests.get(f"{self.base_url}/files", headers=self.headers, timeout=10)
            if response.status_code == 200:
                files = response.json()
                file_count = len(files.get('files', []))
                self.print_test("API Authentication", "PASS", f"Access granted, {file_count} files found")
                return True
            elif response.status_code == 401:
                self.print_test("API Authentication", "FAIL", "Invalid API key")
                return False
            else:
                self.print_test("API Authentication", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_test("API Authentication", "FAIL", f"Connection error: {str(e)}")
            return False
            
    def test_file_upload(self):
        """Test file upload functionality"""
        self.print_header("FILE UPLOAD TEST")
        
        # Create a test file
        test_content = f"VRCPhoto2URL Upload Test - {datetime.now().isoformat()}"
        test_filename = f"upload_test_{int(time.time())}.txt"
        
        try:
            files = {'file': (test_filename, test_content.encode(), 'text/plain')}
            response = requests.post(f"{self.base_url}/upload", 
                                   headers=self.headers, files=files, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    file_id = data.get('file_id')
                    file_url = data.get('url')
                    self.print_test("File Upload", "PASS", 
                                  f"File ID: {file_id[:8]}..., URL: {file_url[:50]}...")
                    return file_id
                else:
                    self.print_test("File Upload", "FAIL", "Upload failed in response")
                    return None
            else:
                self.print_test("File Upload", "FAIL", f"HTTP {response.status_code}")
                return None
        except Exception as e:
            self.print_test("File Upload", "FAIL", f"Upload error: {str(e)}")
            return None
            
    def test_file_download(self, file_id):
        """Test file download functionality"""
        if not file_id:
            self.print_test("File Download", "SKIP", "No file ID from upload test")
            return False
            
        try:
            response = requests.get(f"{self.base_url}/files/{file_id}", timeout=10)
            if response.status_code == 200:
                content_length = len(response.content)
                self.print_test("File Download", "PASS", f"Downloaded {content_length} bytes")
                return True
            else:
                self.print_test("File Download", "FAIL", f"HTTP {response.status_code}")
                return False
        except Exception as e:
            self.print_test("File Download", "FAIL", f"Download error: {str(e)}")
            return False
            
    def test_web_interfaces(self):
        """Test web interface accessibility"""
        self.print_header("WEB INTERFACE ACCESS")
        
        interfaces = [
            ("Main Page", "/"),
            ("Admin Interface", "/admin"),
            ("Enhanced Admin", "/admin/enhanced"),
            ("Web Client", "/client"),
            ("Login Page", "/admin/login"),
            ("API Documentation", "/docs")
        ]
        
        for name, endpoint in interfaces:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code == 200:
                    content_length = len(response.content)
                    self.print_test(f"{name}", "PASS", f"{content_length} bytes loaded")
                else:
                    self.print_test(f"{name}", "FAIL", f"HTTP {response.status_code}")
            except Exception as e:
                self.print_test(f"{name}", "FAIL", f"Error: {str(e)}")
                
    def test_client_config(self):
        """Test client configuration file"""
        self.print_header("CLIENT CONFIGURATION")
        
        config_path = Path("client/client_config.json")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                
                # Check server URL
                if config.get('server_url') == self.base_url:
                    self.print_test("Server URL", "PASS", config['server_url'])
                else:
                    self.print_test("Server URL", "FAIL", f"Mismatch: {config.get('server_url')}")
                
                # Check API key
                if config.get('api_key') == self.api_key:
                    self.print_test("API Key", "PASS", "Correct API key configured")
                else:
                    self.print_test("API Key", "FAIL", "API key mismatch")
                    
                # Check other settings
                settings = ['auto_upload', 'vrchat_mode', 'remember_connection']
                for setting in settings:
                    value = config.get(setting, False)
                    status = "PASS" if value else "WARN"
                    self.print_test(f"{setting.replace('_', ' ').title()}", status, str(value))
                    
            except Exception as e:
                self.print_test("Config File", "FAIL", f"Error reading config: {str(e)}")
        else:
            self.print_test("Config File", "FAIL", "client_config.json not found")
            
    def generate_summary(self):
        """Generate test summary"""
        self.print_header("TEST SUMMARY")
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        skipped_tests = len([r for r in self.test_results if r['status'] in ['SKIP', 'WARN']])
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"⚠️  Warnings/Skipped: {skipped_tests}")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if failed_tests == 0:
            print(f"\n🎉 ALL TESTS PASSED! VRCPhoto2URL is fully operational!")
            print(f"🚀 System ready for production use!")
        else:
            print(f"\n⚠️  {failed_tests} test(s) failed. Please review the issues above.")
            
        return failed_tests == 0
        
    def run_all_tests(self):
        """Run all verification tests"""
        print("🧪 VRCPhoto2URL Connection & Upload Verification")
        print("=" * 60)
        print(f"🌐 Server: {self.base_url}")
        print(f"🔑 API Key: {'*' * (len(self.api_key) - 8)}{self.api_key[-8:]}")
        print(f"⏰ Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all tests
        self.test_server_health()
        self.test_api_authentication()
        uploaded_file_id = self.test_file_upload()
        self.test_file_download(uploaded_file_id)
        self.test_web_interfaces()
        self.test_client_config()
        
        # Generate summary
        return self.generate_summary()

def main():
    """Main function to run verification tests"""
    verifier = VRCPhoto2URLVerification()
    success = verifier.run_all_tests()
    
    if success:
        print(f"\n✨ Verification complete! VRCPhoto2URL is ready to use.")
        print(f"🎮 Launch client: python scripts/launch_client.py")
        print(f"🌐 Admin access: {verifier.base_url}/admin/enhanced")
    else:
        print(f"\n🔧 Some issues were found. Please review and fix the failed tests.")
        
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())

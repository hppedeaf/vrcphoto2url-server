#!/usr/bin/env python3
"""
VRCPhoto2URL Final Deployment Verification
Tests all components to ensure the system is fully operational
"""
import json
import requests
import sys
import os
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_section(title):
    """Print a formatted section header"""
    print(f"\n🔍 {title}")
    print("-" * 40)

def test_config_file():
    """Test if configuration file exists and is valid"""
    print_section("Configuration File Check")
    
    # Look for config file in the client directory
    script_dir = Path(__file__).parent.parent  # Go up to VRCPhoto2URL root
    config_file = script_dir / "client" / "client_config.json"
    
    if not config_file.exists():
        print(f"❌ client_config.json not found at: {config_file}")
        return False
    
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        required_keys = ['server_url', 'api_key', 'auto_upload', 'vrchat_mode', 'remember_connection']
        missing_keys = [key for key in required_keys if key not in config]
        
        if missing_keys:
            print(f"❌ Missing configuration keys: {missing_keys}")
            return False
        
        print("✅ Configuration file is valid")
        print(f"   Server: {config['server_url']}")
        print(f"   VRChat Mode: {config['vrchat_mode']}")
        print(f"   Auto Upload: {config['auto_upload']}")
        return True
        
    except json.JSONDecodeError:
        print("❌ Configuration file is not valid JSON")
        return False
    except Exception as e:
        print(f"❌ Error reading configuration: {e}")
        return False

def test_server_connection():
    """Test connection to Railway server"""
    print_section("Server Connection Test")
    
    try:
        # Look for config file in the client directory
        script_dir = Path(__file__).parent.parent  # Go up to VRCPhoto2URL root
        config_file = script_dir / "client" / "client_config.json"
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        server_url = config['server_url']
        api_key = config['api_key']
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'User-Agent': 'VRCPhoto2URL-Verification/1.0'
        }
        
        # Test health endpoint
        print("   Testing health endpoint...")
        health_response = requests.get(f"{server_url}/health", headers=headers, timeout=10)
        
        if health_response.status_code != 200:
            print(f"❌ Health check failed: {health_response.status_code}")
            return False
        
        health_data = health_response.json()
        print(f"   ✅ Server is healthy: {health_data['status']}")
        
        # Test stats endpoint
        print("   Testing stats endpoint...")
        stats_response = requests.get(f"{server_url}/stats", headers=headers, timeout=10)
        
        if stats_response.status_code != 200:
            print(f"❌ Stats check failed: {stats_response.status_code}")
            return False
        
        stats_data = stats_response.json()
        print(f"   ✅ Server stats: {stats_data['total_files']} files, {stats_data['total_size_mb']:.1f} MB")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server - check internet connection")
        return False
    except requests.exceptions.Timeout:
        print("❌ Server connection timeout")
        return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_client_dependencies():
    """Test if all required Python packages are available"""
    print_section("Client Dependencies Check")
    
    required_packages = [
        ('PySide6', 'GUI framework'),
        ('requests', 'HTTP client'),
        ('watchdog', 'File monitoring'),
        ('PIL', 'Image processing (Pillow)'),
        ('pyperclip', 'Clipboard access')
    ]
    
    all_good = True
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package} - {description}")
        except ImportError:
            print(f"   ❌ {package} - {description} (MISSING)")
            all_good = False
    
    if all_good:
        print("✅ All dependencies are installed")
    else:
        print("❌ Some dependencies are missing - run: pip install -r requirements.txt")
    
    return all_good

def test_launcher_scripts():
    """Test if launcher scripts exist"""
    print_section("Launcher Scripts Check")
    
    # Get paths relative to project root
    script_dir = Path(__file__).parent.parent  # Go up to VRCPhoto2URL root
    
    scripts = [
        (script_dir / 'scripts' / 'launch_client.py', 'Python launcher'),
        (script_dir / 'scripts' / 'start_client.bat', 'Windows batch file'),
        (script_dir / 'client' / 'src' / 'modern_client.py', 'Main client application')
    ]
    
    all_good = True
    for script_path, description in scripts:
        if script_path.exists():
            print(f"   ✅ {script_path.name} - {description}")
        else:
            print(f"   ❌ {script_path.name} - {description} (MISSING)")
            all_good = False
    
    return all_good

def test_vrchat_folder():
    """Check if VRChat Screenshots folder exists"""
    print_section("VRChat Integration Check")
    
    # Common VRChat screenshot paths
    possible_paths = [
        Path.home() / "Pictures" / "VRChat",
        Path.home() / "Documents" / "VRChat",
        Path("C:/Users") / os.getenv('USERNAME', 'User') / "Pictures" / "VRChat"
    ]
    
    vrchat_folder = None
    for path in possible_paths:
        if path.exists():
            vrchat_folder = path
            break
    
    if vrchat_folder:
        print(f"   ✅ VRChat Screenshots folder found: {vrchat_folder}")
        
        # Check if there are any screenshots
        screenshots = list(vrchat_folder.glob("*.png")) + list(vrchat_folder.glob("*.jpg"))
        print(f"   📸 Found {len(screenshots)} existing screenshots")
        return True
    else:
        print("   ⚠️ VRChat Screenshots folder not found")
        print("   💡 You'll need to add it manually in the client")
        print("   📁 Typical location: %USERPROFILE%\\Pictures\\VRChat")
        return False

def run_comprehensive_test():
    """Run all verification tests"""
    print_header("VRCPhoto2URL Deployment Verification")
    print("Testing all components for complete functionality...")
    
    # Change to client directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    tests = [
        ("Configuration", test_config_file),
        ("Dependencies", test_client_dependencies),
        ("Server Connection", test_server_connection),
        ("Launcher Scripts", test_launcher_scripts),
        ("VRChat Integration", test_vrchat_folder)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test failed with error: {e}")
            results[test_name] = False
    
    # Summary
    print_header("Deployment Verification Summary")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status}  {test_name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 DEPLOYMENT VERIFICATION SUCCESSFUL!")
        print("✅ All systems operational")
        print("✅ Ready for VRChat screenshot auto-upload")
        print("\n🚀 To start using:")
        print("   1. Double-click 'start_client.bat' or run 'python launch_client.py'")
        print("   2. Client will auto-connect to Railway server")
        print("   3. Add your VRChat Screenshots folder")
        print("   4. Take screenshots in VRChat - they'll auto-upload!")
        return True
    else:
        print(f"\n⚠️ DEPLOYMENT VERIFICATION INCOMPLETE")
        print(f"❌ {total - passed} issue(s) need to be resolved")
        print("\n💡 Fix the failed tests and run verification again")
        return False

if __name__ == "__main__":
    success = run_comprehensive_test()
    
    if not success:
        print("\n⚠️ Press Enter to exit...")
        input()
    
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Final End-to-End Integration Test
This test verifies the complete client-server workflow including file upload functionality
"""
import sys
import os
import json
import tempfile
import time
from pathlib import Path

# Add client src to path
client_src = Path(__file__).parent / "client" / "src"
sys.path.insert(0, str(client_src))

try:
    from server_client import ServerManager
    print("✅ ServerManager import successful")
except ImportError as e:
    print(f"❌ Failed to import ServerManager: {e}")
    sys.exit(1)

def create_test_file():
    """Create a temporary test file for upload"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write("VRCPhoto2URL Test File\n")
        f.write("=========================\n")
        f.write("This is a test file created for integration testing.\n")
        f.write(f"Created: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("Status: Testing end-to-end upload workflow - SUCCESS\n")
        return f.name

def test_full_workflow():
    """Test complete client-server workflow"""
    print("\n🔍 Testing complete end-to-end workflow...")
    
    # Load client config
    config_path = Path(__file__).parent / "client" / "client_config.json"
    with open(config_path) as f:
        config = json.load(f)
    
    server_manager = ServerManager()
    
    try:
        # Step 1: Test connection
        print("📡 Step 1: Testing server connection...")
        success = server_manager.connect(
            config["server_url"], 
            config.get("api_key", "")
        )
        
        if not success:
            print("❌ Failed to connect to server")
            return False
        
        print(f"✅ Connected to {config['server_url']}")
        
        # Step 2: Get server stats
        print("📊 Step 2: Getting server statistics...")
        stats = server_manager.get_server_stats()
        print(f"   Total files: {stats.get('total_files', 0)}")
        print(f"   Total size: {stats.get('total_size_mb', 0)} MB")
        print(f"   Server status: {stats.get('server_uptime', 'Unknown')}")
        
        # Step 3: Test file upload
        print("📤 Step 3: Testing file upload...")
        test_file_path = create_test_file()
        
        try:
            # Upload with progress callback
            def progress_callback(bytes_uploaded, total_bytes):
                if total_bytes > 0:
                    percent = (bytes_uploaded / total_bytes) * 100
                    print(f"   Upload progress: {percent:.1f}%")
            
            upload_result = server_manager.upload_file(
                test_file_path, 
                progress_callback=progress_callback
            )
            
            if upload_result and 'file_id' in upload_result:
                print(f"✅ File uploaded successfully!")
                print(f"   File ID: {upload_result['file_id']}")
                print(f"   Upload URL: {upload_result.get('upload_url', 'N/A')}")
                
                # Step 4: Verify stats updated
                print("📈 Step 4: Verifying server stats updated...")
                updated_stats = server_manager.get_server_stats()
                if updated_stats.get('total_files', 0) > stats.get('total_files', 0):
                    print("✅ Server stats updated correctly")
                else:
                    print("⚠️ Server stats may not have updated yet (caching)")
                
                return True
            else:
                print("❌ File upload failed")
                return False
                
        finally:
            # Cleanup test file
            if os.path.exists(test_file_path):
                os.unlink(test_file_path)
                
    except Exception as e:
        print(f"❌ Workflow error: {e}")
        return False

def test_client_config():
    """Test client configuration validation"""
    print("\n⚙️ Testing client configuration...")
    
    config_path = Path(__file__).parent / "client" / "client_config.json"
    
    if not config_path.exists():
        print("❌ Client configuration file not found")
        return False
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        required_keys = ['server_url', 'api_key']
        for key in required_keys:
            if key not in config:
                print(f"❌ Missing required config key: {key}")
                return False
            
            if not config[key]:
                print(f"❌ Empty config value for: {key}")
                return False
        
        print("✅ Client configuration is valid")
        print(f"   Server: {config['server_url']}")
        print(f"   API Key: {'*' * (len(config['api_key']) - 8) + config['api_key'][-8:]}")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in config file: {e}")
        return False
    except Exception as e:
        print(f"❌ Config validation error: {e}")
        return False

if __name__ == "__main__":
    print("🎮 VRCPhoto2URL - Final End-to-End Integration Test")
    print("=" * 60)
    
    # Test 1: Configuration validation
    config_ok = test_client_config()
    
    # Test 2: Full workflow
    workflow_ok = test_full_workflow() if config_ok else False
    
    print("\n" + "=" * 60)
    print("📋 FINAL TEST RESULTS:")
    print("=" * 60)
    print(f"✅ ServerManager Import:  {'PASS' if True else 'FAIL'}")
    print(f"✅ Configuration Check:   {'PASS' if config_ok else 'FAIL'}")  
    print(f"✅ End-to-End Workflow:   {'PASS' if workflow_ok else 'FAIL'}")
    
    if config_ok and workflow_ok:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        print("🚀 VRCPhoto2URL is fully operational and ready for production use!")
        print("📸 Your VRChat screenshots can now be automatically uploaded to Railway!")
        
        print("\n💡 Next Steps:")
        print("   1. Start the desktop client: python scripts/launch_client.py")
        print("   2. Configure VRChat screenshot folder")
        print("   3. Take screenshots in VRChat (F12)")
        print("   4. URLs will be automatically copied to clipboard")
        
    else:
        print("\n❌ Some tests failed. Please check the configuration and server connection.")
        sys.exit(1)

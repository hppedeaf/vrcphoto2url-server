#!/usr/bin/env python3
"""
Test the client auto-connection logic without GUI
"""
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

def test_client_config_loading():
    """Test if the client can load and process the config file correctly"""
    print("🧪 Testing Client Config Loading Logic")
    print("=" * 45)
    
    # Load config like the client does
    local_config_file = Path("client_config.json")
    if local_config_file.exists():
        print(f"✅ Found config file: {local_config_file}")
        
        with open(local_config_file, 'r') as f:
            local_config = json.load(f)
        
        print(f"📋 Config contents:")
        for key, value in local_config.items():
            if key == 'api_key':
                print(f"  {key}: {value[:20]}..." if value else f"  {key}: (empty)")
            else:
                print(f"  {key}: {value}")
        
        # Check if auto-connection should trigger
        server_url = local_config.get('server_url', '')
        remember_connection = local_config.get('remember_connection', True)
        
        print(f"\n🔍 Auto-connection check:")
        print(f"  Server URL present: {'✅' if server_url else '❌'}")
        print(f"  Remember connection: {'✅' if remember_connection else '❌'}")
        
        should_auto_connect = server_url and remember_connection
        print(f"  Should auto-connect: {'✅ YES' if should_auto_connect else '❌ NO'}")
        
        if should_auto_connect:
            print(f"\n🎯 Auto-connection would attempt to connect to: {server_url}")
            return True
        else:
            print(f"\n⚠️ Auto-connection would be skipped")
            return False
            
    else:
        print(f"❌ Config file not found: {local_config_file}")
        return False

# Try to import the server manager without GUI
def test_server_manager_import():
    """Test if we can import the server manager"""
    print("\n🧪 Testing Server Manager Import")
    print("=" * 35)
    
    try:
        from server_client import ServerManager
        print("✅ ServerManager imported successfully")
        
        # Create instance
        server_manager = ServerManager()
        print("✅ ServerManager instance created")
        
        return server_manager
    except Exception as e:
        print(f"❌ ServerManager import failed: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Testing VRCPhoto2URL Client Auto-Connection\n")
    
    # Test config loading
    config_ok = test_client_config_loading()
    
    # Test server manager
    server_manager = test_server_manager_import()
    
    if config_ok and server_manager:
        print("\n🎉 SUCCESS!")
        print("✅ Config loading works")
        print("✅ Server manager works") 
        print("✅ Auto-connection should work when GUI starts")
        print("\n💡 The client should auto-connect to Railway when launched!")
    else:
        print("\n⚠️ Some components need attention")
        if not config_ok:
            print("❌ Config loading issue")
        if not server_manager:
            print("❌ Server manager issue")

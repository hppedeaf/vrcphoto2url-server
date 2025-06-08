#!/usr/bin/env python3
"""
Test script to verify client integration with Railway server
"""
import sys
import os
import json
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

# Test server connection
def test_connection():
    print("\n🔍 Testing server connection...")
    
    # Load client config
    config_path = Path(__file__).parent / "client" / "client_config.json"
    with open(config_path) as f:
        config = json.load(f)
    
    server_manager = ServerManager()
    
    try:
        success = server_manager.connect(
            config["server_url"], 
            config.get("api_key", "")
        )
        
        if success:
            print(f"✅ Successfully connected to {config['server_url']}")
            
            # Test server stats
            stats = server_manager.get_server_stats()
            print(f"📊 Server stats: {stats}")
            
            return True
        else:
            print("❌ Failed to connect to server")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    print("🎮 VRCPhoto2URL Client Integration Test")
    print("=" * 50)
    
    success = test_connection()
    
    if success:
        print("\n✅ All integration tests passed!")
        print("🚀 Client is ready for production use")
    else:
        print("\n❌ Integration tests failed")
        sys.exit(1)

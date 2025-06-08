#!/usr/bin/env python3
"""
Quick Demo Setup for VRCPhoto2URL
Sets up a demo configuration for immediate testing
"""
import json
import sys
from pathlib import Path

def setup_demo_config():
    """Setup demo configuration for testing"""
    print("🎮 VRCPhoto2URL - Quick Demo Setup")
    print("=" * 50)
    print("Setting up demo configuration for immediate testing...")
    
    # Demo configuration
    config = {
        "server_url": "https://vrcphoto2url-server-production.up.railway.app",
        "api_key": "demo-key-for-testing",
        "auto_upload": True,
        "vrchat_mode": True,
        "remember_connection": True,
        "upload_timeout": 30,
        "retry_attempts": 3,
        "check_interval": 2
    }
    
    script_dir = Path(__file__).parent
    config_file = script_dir / "client" / "client_config.json"
    
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Demo configuration saved to: {config_file}")
        print(f"🌐 Server URL: {config['server_url']}")
        print(f"🔑 API Key: {config['api_key']}")
        
        print("\n⚠️  Note: This is a demo configuration")
        print("   For production use, run: python setup_config.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving demo configuration: {e}")
        return False

if __name__ == "__main__":
    setup_demo_config()

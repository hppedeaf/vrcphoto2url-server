#!/usr/bin/env python3
"""
Test auto-connection functionality without GUI
"""
import json
import requests
from pathlib import Path

def test_auto_connection():
    """Test the auto-connection to Railway server"""
    print("🧪 Testing Auto-Connection to Railway Server")
    print("=" * 50)
    
    # Load config file
    config_file = Path("client_config.json")
    if not config_file.exists():
        print("❌ client_config.json not found!")
        return False
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    server_url = config.get('server_url', '')
    api_key = config.get('api_key', '')
    
    print(f"📡 Server URL: {server_url}")
    print(f"🔑 API Key: {api_key[:20]}..." if api_key else "🔑 No API key")
    print()
    
    # Test connection
    try:
        headers = {
            'User-Agent': 'VRCPhoto2URL-Test-Client/1.0',
            'Authorization': f'Bearer {api_key}' if api_key else ''
        }
        
        print("🔍 Testing health endpoint...")
        response = requests.get(f"{server_url}/health", headers=headers, timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check: {health_data}")
            
            # Test stats endpoint
            print("\n🔍 Testing stats endpoint...")
            stats_response = requests.get(f"{server_url}/stats", headers=headers, timeout=10)
            
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                print(f"✅ Stats: {stats_data}")
                print(f"\n🎉 Connection successful!")
                print(f"📊 Server has {stats_data.get('total_files', 0)} files")
                print(f"💾 Total storage: {stats_data.get('total_size_mb', 0)}MB")
                return True
            else:
                print(f"⚠️ Stats endpoint returned: {stats_response.status_code}")
                return False
                
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - server unreachable")
        return False
    except requests.exceptions.Timeout:
        print("❌ Connection timeout")
        return False
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_auto_connection()
    if success:
        print("\n🚀 Auto-connection functionality working!")
        print("✅ The client should now auto-connect when launched")
    else:
        print("\n💥 Auto-connection test failed")
        print("❌ Check server URL and API key")

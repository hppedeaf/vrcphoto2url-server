#!/usr/bin/env python3
"""
VRCPhoto2URL Configuration Setup
Interactive setup for client configuration
"""
import sys
import os
import json
import secrets
from pathlib import Path

def generate_api_key():
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)

def get_railway_url():
    """Get Railway URL from user"""
    print("\n🌐 Server Configuration")
    print("=" * 50)
    
    print("\n📝 Enter your Railway server URL:")
    print("   Example: https://vrcphoto2url-production-a1b2c3.railway.app")
    print("   (Get this from your Railway project dashboard)")
    
    while True:
        url = input("\n🔗 Server URL: ").strip()
        
        if not url:
            print("❌ URL cannot be empty")
            continue
            
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        if 'railway.app' in url or 'localhost' in url:
            return url
        else:
            print("⚠️  Are you sure this is correct? (y/n)")
            confirm = input().strip().lower()
            if confirm in ['y', 'yes']:
                return url

def get_api_key():
    """Get API key from user"""
    print("\n🔐 API Key Configuration")
    print("=" * 50)
    
    print("\n📝 Choose an option:")
    print("   1. Generate a new secure API key (recommended)")
    print("   2. Enter your own API key")
    print("   3. Use for local testing (demo key)")
    
    while True:
        choice = input("\n🔢 Choice (1-3): ").strip()
        
        if choice == '1':
            api_key = generate_api_key()
            print(f"\n✨ Generated API key: {api_key}")
            print("\n⚠️  IMPORTANT: Set this same API key in your Railway environment variables!")
            print("   Railway Dashboard → Your Project → Variables → API_KEY")
            return api_key
            
        elif choice == '2':
            api_key = input("\n🔑 Enter your API key: ").strip()
            if api_key:
                return api_key
            else:
                print("❌ API key cannot be empty")
                
        elif choice == '3':
            return "demo-key-for-local-testing-only"
            
        else:
            print("❌ Please enter 1, 2, or 3")

def save_config(server_url, api_key):
    """Save configuration to file"""
    config = {
        "server_url": server_url,
        "api_key": api_key,
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
        
        print(f"\n✅ Configuration saved to: {config_file}")
        return True
        
    except Exception as e:
        print(f"\n❌ Error saving configuration: {e}")
        return False

def test_configuration():
    """Test the saved configuration"""
    print("\n🧪 Testing Configuration")
    print("=" * 50)
    
    try:
        import requests
        
        script_dir = Path(__file__).parent
        config_file = script_dir / "client" / "client_config.json"
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        server_url = config['server_url']
        api_key = config['api_key']
        
        print(f"🔗 Testing connection to: {server_url}")
        
        # Test health endpoint
        health_url = f"{server_url}/health"
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Server is responding")
            data = response.json()
            print(f"   Status: {data.get('status', 'unknown')}")
            return True
        else:
            print(f"❌ Server returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server")
        print("   Check your internet connection and server URL")
        return False
    except requests.exceptions.Timeout:
        print("❌ Connection timeout")
        return False
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🎮 VRCPhoto2URL Configuration Setup")
    print("=" * 50)
    print("This wizard will help you configure your VRCPhoto2URL client")
    
    # Check if already configured
    script_dir = Path(__file__).parent
    config_file = script_dir / "client" / "client_config.json"
    
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            if (config.get('server_url') != 'https://your-app.railway.app' and 
                config.get('api_key') != 'your-api-key-here'):
                print("\n✅ Configuration already exists:")
                print(f"   Server: {config.get('server_url')}")
                print(f"   API Key: {'*' * 20}...{config.get('api_key', '')[-4:]}")
                
                print("\n🔄 Do you want to reconfigure? (y/n)")
                reconfigure = input().strip().lower()
                if reconfigure not in ['y', 'yes']:
                    print("👍 Using existing configuration")
                    return test_configuration()
        except:
            pass
    
    # Get configuration from user
    server_url = get_railway_url()
    api_key = get_api_key()
    
    # Save configuration
    if save_config(server_url, api_key):
        print("\n🎉 Configuration completed successfully!")
        
        # Test configuration
        print("\n🧪 Would you like to test the connection? (y/n)")
        test_choice = input().strip().lower()
        if test_choice in ['y', 'yes']:
            test_configuration()
        
        print("\n🚀 Ready to launch client!")
        print("   Run: python scripts/launch_client.py")
        print("   Or:  scripts/start_client.bat")
        
        return True
    else:
        print("\n❌ Configuration setup failed")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Setup failed: {e}")
        sys.exit(1)

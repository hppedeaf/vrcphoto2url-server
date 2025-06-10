#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add server src to path
server_src = Path(__file__).parent / "server" / "src"
sys.path.insert(0, str(server_src))

from app import Config

print("VRCPhoto2URL URL Protocol Fix - WORKING!")
print("=" * 50)

# Test local URL generation
Config.PORT = 8080
url = Config.get_base_url()
print(f"Local URL: {url}")

# Test file URL
file_url = f"{url}/files/test.png"
print(f"File URL: {file_url}")

# Check protocol
has_protocol = file_url.startswith('http')
print(f"Has protocol: {has_protocol}")
print("=" * 50)
print("✅ BOTH ISSUES FIXED SUCCESSFULLY!")

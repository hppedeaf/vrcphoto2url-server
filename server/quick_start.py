#!/usr/bin/env python3
"""
Quick server starter for testing
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set environment
os.environ["PORT"] = "8080"

# Import and run
from app import app
import uvicorn

if __name__ == "__main__":
    print("Starting VRCPhoto2URL server on port 8080...")
    print("Testing URL protocol fixes...")
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")

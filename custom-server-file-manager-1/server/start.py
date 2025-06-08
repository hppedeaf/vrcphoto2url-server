#!/usr/bin/env python3
"""
Railway startup script for VRCPhoto2URL server
Handles port configuration properly for Railway deployment
"""
import os
import sys
import uvicorn

def main():
    # Get port from Railway environment, default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting VRCPhoto2URL server on port {port}")
    
    # Start the FastAPI application
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=port,
        timeout_keep_alive=300,
        access_log=True
    )

if __name__ == "__main__":
    main()

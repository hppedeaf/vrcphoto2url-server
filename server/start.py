#!/usr/bin/env python3
"""
Railway startup script for VRCPhoto2URL server
Handles port configuration properly for Railway deployment
"""
import os
import sys
import uvicorn

def main():
    # Get port from Railway environment, default to 8080 for testing
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"Starting VRCPhoto2URL server on {host}:{port}")
    print(f"Public URL: {os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'http://localhost:8000')}")
    
    # Start the FastAPI application
    uvicorn.run(
        "src.app:app",
        host=host,
        port=port,
        timeout_keep_alive=300,
        access_log=True,
        reload=False  # Disable reload in production
    )

if __name__ == "__main__":
    main()

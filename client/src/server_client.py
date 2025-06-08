#!/usr/bin/env python3
"""
Server Client Manager for Custom Server File Manager Client
Handles all server communication and API calls
"""

import requests
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServerError(Exception):
    """Custom exception for server-related errors"""
    pass


class ServerManager:
    """
    Manages connection and communication with the Custom Server File Manager
    """
    
    def __init__(self):
        self.server_url = ""
        self.api_key = ""
        self.connected = False
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'VRCPhoto2URL-Client/2.0',
            'Accept': 'application/json'
        })
        
    def connect(self, server_url: str, api_key: str = "") -> bool:
        """
        Connect to the server with given URL and API key
        
        Args:
            server_url: Server URL (e.g., https://your-server.railway.app)
            api_key: Optional API key for authentication
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Clean and validate URL
            if not server_url:
                raise ServerError("Server URL cannot be empty")
                
            # Ensure URL has protocol
            if not server_url.startswith(('http://', 'https://')):
                server_url = f"http://{server_url}"
                
            # Remove trailing slash
            server_url = server_url.rstrip('/')
            
            self.server_url = server_url
            self.api_key = api_key
            
            # Update session headers
            if api_key:
                self.session.headers.update({
                    'Authorization': f'Bearer {api_key}'
                })
            elif 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']
            
            # Test connection
            response = self.session.get(f"{self.server_url}/health", timeout=10)
            
            if response.status_code == 200:
                self.connected = True
                logger.info(f"Successfully connected to {self.server_url}")
                return True
            else:
                logger.error(f"Health check failed: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            logger.error("Connection failed - server unreachable")
            return False
        except requests.exceptions.Timeout:
            logger.error("Connection timeout")
            return False
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from the server"""
        self.connected = False
        self.server_url = ""
        self.api_key = ""
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
        logger.info("Disconnected from server")
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the current connection and return server info
        
        Returns:
            dict: Server information if successful
        """
        if not self.connected:
            raise ServerError("Not connected to server")
            
        try:
            response = self.session.get(f"{self.server_url}/health", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                raise ServerError(f"Health check failed: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise ServerError(f"Connection test failed: {str(e)}")
    
    def get_server_stats(self) -> Dict[str, Any]:
        """
        Get server statistics
        
        Returns:
            dict: Server statistics
        """
        if not self.connected:
            raise ServerError("Not connected to server")
            
        try:
            response = self.session.get(f"{self.server_url}/stats", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                raise ServerError(f"Stats request failed: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise ServerError(f"Failed to get server stats: {str(e)}")
    
    def upload_file(self, file_path: str, progress_callback=None) -> Dict[str, Any]:
        """
        Upload a file to the server
        
        Args:
            file_path: Path to the file to upload
            progress_callback: Optional callback for upload progress
            
        Returns:
            dict: Upload result
        """
        if not self.connected:
            raise ServerError("Not connected to server")
            
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise ServerError(f"File not found: {file_path}")
            
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'application/octet-stream')}
                
                response = self.session.post(
                    f"{self.server_url}/upload",
                    files=files,
                    timeout=300  # 5 minutes for uploads
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    raise ServerError(f"Upload failed: {response.status_code} - {response.text}")
                    
        except requests.exceptions.RequestException as e:
            raise ServerError(f"Upload failed: {str(e)}")
        except Exception as e:
            raise ServerError(f"Upload error: {str(e)}")
    
    def list_files(self) -> List[Dict[str, Any]]:
        """
        Get list of files from server
        
        Returns:
            list: List of file information
        """
        if not self.connected:
            raise ServerError("Not connected to server")
            
        try:
            response = self.session.get(f"{self.server_url}/files", timeout=30)
            if response.status_code == 200:
                data = response.json()
                return data.get('files', [])
            else:
                raise ServerError(f"File list request failed: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise ServerError(f"Failed to get file list: {str(e)}")
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from the server
        
        Args:
            file_id: ID of the file to delete
            
        Returns:
            bool: True if deletion successful
        """
        if not self.connected:
            raise ServerError("Not connected to server")
            
        try:
            response = self.session.delete(f"{self.server_url}/files/{file_id}", timeout=30)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            raise ServerError(f"Failed to delete file: {str(e)}")
    
    def download_file(self, file_id: str, save_path: str) -> bool:
        """
        Download a file from the server
        
        Args:
            file_id: ID of the file to download
            save_path: Path where to save the downloaded file
            
        Returns:
            bool: True if download successful
        """
        if not self.connected:
            raise ServerError("Not connected to server")
            
        try:
            response = self.session.get(f"{self.server_url}/files/{file_id}", timeout=300)
            if response.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                raise ServerError(f"Download failed: {response.status_code}")
        except requests.exceptions.RequestException as e:
            raise ServerError(f"Failed to download file: {str(e)}")
    
    def get_file_url(self, file_id: str) -> str:
        """
        Get direct URL for a file
        
        Args:
            file_id: ID of the file
            
        Returns:
            str: Direct URL to the file
        """
        if not self.connected:
            raise ServerError("Not connected to server")
            
        return f"{self.server_url}/files/{file_id}"
    
    def is_connected(self) -> bool:
        """Check if currently connected to server"""
        return self.connected
    
    def get_server_url(self) -> str:
        """Get current server URL"""
        return self.server_url
    
    def get_api_key(self) -> str:
        """Get current API key"""
        return self.api_key


# Convenience function for backwards compatibility
def create_server_manager() -> ServerManager:
    """Create and return a new ServerManager instance"""
    return ServerManager()

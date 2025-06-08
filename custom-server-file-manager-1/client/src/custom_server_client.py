#!/usr/bin/env python3
"""
Custom Server Client - Communication with FastAPI Server
Handles all HTTP requests to the server
"""

import os
import requests
import json
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomServerError(Exception):
    """Custom exception for server communication errors"""
    pass

class CustomServerClient:
    """Client for communicating with the Custom Server File Manager API"""
    
    def __init__(self):
        self.base_url = None
        self.api_key = None
        self.session = requests.Session()
        self.connected = False
        
    def connect(self, server_url: str, api_key: str) -> bool:
        """
        Connect to the server
        
        Args:
            server_url: Base URL of the server (e.g., https://your-app.railway.app)
            api_key: API key for authentication
            
        Returns:
            bool: True if connection successful
        """
        try:
            # Clean up URL
            self.base_url = server_url.rstrip('/')
            self.api_key = api_key
            
            # Set authentication header
            self.session.headers.update({
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            })
            
            # Test connection
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                self.connected = True
                logger.info(f"Successfully connected to server: {self.base_url}")
                return True
            else:
                logger.error(f"Server health check failed: {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from server"""
        self.connected = False
        self.base_url = None
        self.api_key = None
        self.session.headers.pop('Authorization', None)
        logger.info("Disconnected from server")
    
    def upload_file(self, file_path: str) -> Tuple[str, str]:
        """
        Upload a file to the server
        
        Args:
            file_path: Path to the file to upload
            
        Returns:
            Tuple[str, str]: (file_url, service_name)
            
        Raises:
            CustomServerError: If upload fails
        """
        if not self.connected:
            raise CustomServerError("Not connected to server")
        
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise CustomServerError(f"File not found: {file_path}")
            
            # Prepare file for upload
            with open(file_path, 'rb') as f:
                files = {
                    'file': (file_path.name, f, self._get_content_type(file_path))
                }
                
                # Remove Content-Type header for multipart upload
                headers = {k: v for k, v in self.session.headers.items() if k != 'Content-Type'}
                
                response = self.session.post(
                    f"{self.base_url}/upload",
                    files=files,
                    headers=headers,
                    timeout=60
                )
            
            if response.status_code == 200:
                data = response.json()
                file_url = data.get('url', '')
                logger.info(f"File uploaded successfully: {file_path.name}")
                return file_url, "Custom Server"
            else:
                error_msg = f"Upload failed: {response.status_code}"
                try:
                    error_detail = response.json().get('detail', 'Unknown error')
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - {response.text}"
                raise CustomServerError(error_msg)
                
        except requests.exceptions.RequestException as e:
            raise CustomServerError(f"Network error during upload: {e}")
        except Exception as e:
            raise CustomServerError(f"Upload error: {e}")
    
    def list_files(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """
        List files on the server
        
        Args:
            limit: Maximum number of files to return
            offset: Number of files to skip
            
        Returns:
            List[Dict]: List of file information
        """
        if not self.connected:
            raise CustomServerError("Not connected to server")
        
        try:
            params = {'limit': limit, 'offset': offset}
            response = self.session.get(
                f"{self.base_url}/files",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('files', [])
            else:
                raise CustomServerError(f"Failed to list files: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise CustomServerError(f"Network error: {e}")
    
    def delete_file(self, file_id: str) -> bool:
        """
        Delete a file from the server
        
        Args:
            file_id: ID of the file to delete
            
        Returns:
            bool: True if deletion successful
        """
        if not self.connected:
            raise CustomServerError("Not connected to server")
        
        try:
            response = self.session.delete(
                f"{self.base_url}/files/{file_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"File deleted successfully: {file_id}")
                return True
            else:
                raise CustomServerError(f"Failed to delete file: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise CustomServerError(f"Network error: {e}")
    
    def _get_content_type(self, file_path: Path) -> str:
        """Get content type based on file extension"""
        extension = file_path.suffix.lower()
        
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.zip': 'application/zip',
            '.rar': 'application/x-rar-compressed',
            '.7z': 'application/x-7z-compressed',
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav'
        }
        
        return content_types.get(extension, 'application/octet-stream')

class CustomServerManager:
    """Manager class for backward compatibility with existing code"""
    
    def __init__(self):
        self.client = CustomServerClient()
        self.active_service = None
    
    def authenticate_service(self, service_name: str, credentials: Dict) -> bool:
        """Authenticate with the service"""
        if service_name == "custom":
            server_url = credentials.get('server_url', '')
            api_key = credentials.get('api_key', '')
            
            if self.client.connect(server_url, api_key):
                self.active_service = self.client
                return True
        return False
    
    def disconnect_service(self):
        """Disconnect from service"""
        if self.client:
            self.client.disconnect()
        self.active_service = None
    
    def upload_file(self, file_path: str) -> Tuple[str, str]:
        """Upload file using active service"""
        if self.active_service:
            return self.active_service.upload_file(file_path)
        raise CustomServerError("No active service")
    
    def is_connected(self) -> bool:
        """Check if connected to any service"""
        return self.active_service is not None and self.active_service.connected
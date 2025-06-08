#!/usr/bin/env python3
"""
Server Client Manager for Custom Server File Manager
Handles communication with the server API
"""

import os
import requests
import json
from typing import Optional, Dict, Any
from urllib.parse import urljoin

class ServerError(Exception):
    """Custom server error exception"""
    pass

class ServerManager:
    """Manages communication with the Custom Server File Manager server"""
    
    def __init__(self):
        self.server_url = None
        self.api_key = None
        self.session = None
        self.connected = False
        
    def connect(self, server_url: str, api_key: str = "") -> bool:
        """Connect to the server"""
        try:
            # Clean up URL
            if not server_url.startswith(('http://', 'https://')):
                server_url = f"http://{server_url}"
            
            if not server_url.endswith('/'):
                server_url += '/'
            
            self.server_url = server_url
            self.api_key = api_key
            
            # Create session
            self.session = requests.Session()
            
            # Set headers
            headers = {
                'User-Agent': 'Custom-Server-File-Manager-Client/2.0'
            }
            
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
            
            self.session.headers.update(headers)
            
            # Test connection
            response = self.session.get(
                urljoin(self.server_url, 'health'),
                timeout=10
            )
            
            if response.status_code == 200:
                self.connected = True
                return True
            else:
                raise ServerError(f"Server returned status {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            raise ServerError("Could not connect to server. Check URL and network connection.")
        except requests.exceptions.Timeout:
            raise ServerError("Connection timeout. Server may be unavailable.")
        except Exception as e:
            raise ServerError(f"Connection failed: {str(e)}")
    
    def disconnect(self):
        """Disconnect from server"""
        if self.session:
            self.session.close()
            self.session = None
        
        self.connected = False
        self.server_url = None
        self.api_key = None
    
    def test_connection(self) -> Dict[str, Any]:
        """Test server connection and return server info"""
        if not self.connected:
            raise ServerError("Not connected to server")
        
        try:
            response = self.session.get(
                urljoin(self.server_url, 'health'),
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise ServerError(f"Health check failed: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise ServerError(f"Connection test failed: {str(e)}")
    
    def upload_file(self, filepath: str) -> Dict[str, Any]:
        """Upload a file to the server"""
        if not self.connected:
            raise ServerError("Not connected to server")
        
        if not os.path.exists(filepath):
            raise ServerError(f"File not found: {filepath}")
        
        try:
            filename = os.path.basename(filepath)
            
            with open(filepath, 'rb') as file:
                files = {
                    'file': (filename, file, self._get_content_type(filepath))
                }
                
                # Prepare data
                data = {
                    'filename': filename
                }
                
                # Upload file
                response = self.session.post(
                    urljoin(self.server_url, 'upload'),
                    files=files,
                    data=data,
                    timeout=60  # 60 second timeout for uploads
                )
            
            if response.status_code == 200:
                result = response.json()
                return result
            else:
                error_msg = f"Upload failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if 'detail' in error_data:
                        error_msg = error_data['detail']
                except:
                    pass
                raise ServerError(error_msg)
                
        except requests.exceptions.RequestException as e:
            raise ServerError(f"Upload failed: {str(e)}")
        except Exception as e:
            raise ServerError(f"Upload error: {str(e)}")
    
    def get_files(self) -> list:
        """Get list of uploaded files"""
        if not self.connected:
            raise ServerError("Not connected to server")
        
        try:
            response = self.session.get(
                urljoin(self.server_url, 'admin/files'),
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise ServerError(f"Failed to get files: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise ServerError(f"Failed to get files: {str(e)}")
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a file from the server"""
        if not self.connected:
            raise ServerError("Not connected to server")
        
        try:
            response = self.session.delete(
                urljoin(self.server_url, f'admin/files/{file_id}'),
                timeout=10
            )
            
            return response.status_code == 200
            
        except requests.exceptions.RequestException as e:
            raise ServerError(f"Failed to delete file: {str(e)}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get server statistics"""
        if not self.connected:
            raise ServerError("Not connected to server")
        
        try:
            response = self.session.get(
                urljoin(self.server_url, 'admin/stats'),
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise ServerError(f"Failed to get statistics: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise ServerError(f"Failed to get statistics: {str(e)}")
    
    def _get_content_type(self, filepath: str) -> str:
        """Get content type for file"""
        extension = os.path.splitext(filepath)[1].lower()
        
        content_types = {
            # Images
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.tiff': 'image/tiff',
            '.tif': 'image/tiff',
            
            # Videos
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime',
            '.wmv': 'video/x-ms-wmv',
            '.flv': 'video/x-flv',
            '.mkv': 'video/x-matroska',
            '.m4v': 'video/x-m4v',
            
            # Audio
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.flac': 'audio/flac',
            '.aac': 'audio/aac',
            '.ogg': 'audio/ogg',
            '.wma': 'audio/x-ms-wma',
            
            # Documents
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            
            # Archives
            '.zip': 'application/zip',
            '.rar': 'application/x-rar-compressed',
            '.7z': 'application/x-7z-compressed',
        }
        
        return content_types.get(extension, 'application/octet-stream')
    
    def is_connected(self) -> bool:
        """Check if connected to server"""
        return self.connected
    
    def get_server_url(self) -> Optional[str]:
        """Get current server URL"""
        return self.server_url
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        if not self.connected:
            return {"connected": False}
        
        try:
            health_info = self.test_connection()
            return {
                "connected": True,
                "server_url": self.server_url,
                "has_api_key": bool(self.api_key),
                "server_info": health_info
            }
        except:
            return {
                "connected": False,
                "server_url": self.server_url,
                "has_api_key": bool(self.api_key),
                "error": "Cannot reach server"
            }

#!/usr/bin/env python3
"""
Custom Server File Manager - Server Application
A FastAPI-based file server designed for Railway deployment
"""

import os
import uuid
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging

from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
from PIL import Image
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get the project root directory (one level up from src)
project_root = Path(__file__).parent.parent

# Models
class FileInfo(BaseModel):
    file_id: str
    original_filename: str
    filename: str
    url: str
    file_size: int
    upload_time: str
    file_type: str

class UploadResponse(BaseModel):
    success: bool
    file_id: str
    url: str
    original_filename: str
    file_size: int
    message: str

class DeleteResponse(BaseModel):
    success: bool
    message: str

class ListFilesResponse(BaseModel):
    files: List[FileInfo]
    total_count: int

# Configuration
class Config:
    # Server settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", 8000))
    
    # Storage settings
    UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(project_root / "uploads")))
    THUMBNAILS_DIR = UPLOAD_DIR / "thumbnails"
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    
    # Security
    API_KEY = os.getenv("API_KEY", "your-secret-api-key-change-this")
    
    # Allowed file types
    ALLOWED_EXTENSIONS = {
        'images': {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'},
        'documents': {'.pdf', '.doc', '.docx', '.txt', '.rtf'},
        'archives': {'.zip', '.rar', '.7z', '.tar', '.gz'},
        'others': {'.mp4', '.avi', '.mov', '.mp3', '.wav'}
    }
    
    # Railway URL (will be set automatically by Railway)
    BASE_URL = os.getenv("RAILWAY_STATIC_URL", f"http://localhost:{PORT}")

# Initialize FastAPI
app = FastAPI(
    title="Custom Server File Manager",
    description="A file management server for Railway deployment",
    version="1.0.0"
)

# Get the project root directory (one level up from src)
project_root = Path(__file__).parent.parent

# Mount static files and templates
app.mount("/static", StaticFiles(directory=str(project_root / "static")), name="static")
templates = Jinja2Templates(directory=str(project_root / "templates"))

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key"""
    if credentials.credentials != Config.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return True

# Ensure upload directories exist
Config.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
Config.THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

# File storage functions
def save_file_metadata(file_id: str, metadata: Dict[str, Any]):
    """Save file metadata to JSON"""
    metadata_file = Config.UPLOAD_DIR / f"{file_id}.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

def load_file_metadata(file_id: str) -> Optional[Dict[str, Any]]:
    """Load file metadata from JSON"""
    metadata_file = Config.UPLOAD_DIR / f"{file_id}.json"
    if metadata_file.exists():
        with open(metadata_file, 'r') as f:
            return json.load(f)
    return None

def get_all_files() -> List[Dict[str, Any]]:
    """Get all file metadata"""
    files = []
    for json_file in Config.UPLOAD_DIR.glob("*.json"):
        try:
            with open(json_file, 'r') as f:
                metadata = json.load(f)
                files.append(metadata)
        except Exception as e:
            logger.error(f"Error reading metadata file {json_file}: {e}")
    
    # Sort by upload time (newest first)
    files.sort(key=lambda x: x.get('upload_time', ''), reverse=True)
    return files

def create_thumbnail(image_path: Path, thumbnail_path: Path, size: tuple = (200, 200)):
    """Create thumbnail for image"""
    try:
        with Image.open(image_path) as img:
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(thumbnail_path, optimize=True, quality=85)
        return True
    except Exception as e:
        logger.error(f"Error creating thumbnail: {e}")
        return False

def get_file_type(filename: str) -> str:
    """Determine file type category"""
    extension = Path(filename).suffix.lower()
    
    for category, extensions in Config.ALLOWED_EXTENSIONS.items():
        if extension in extensions:
            return category
    return 'other'

def is_allowed_file(filename: str) -> bool:
    """Check if file type is allowed"""
    extension = Path(filename).suffix.lower()
    all_extensions = set()
    for extensions in Config.ALLOWED_EXTENSIONS.values():
        all_extensions.update(extensions)
    return extension in all_extensions

# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Custom Server File Manager API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    auth: bool = Depends(verify_api_key)
):
    """Upload a file"""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        if not is_allowed_file(file.filename):
            raise HTTPException(status_code=400, detail="File type not allowed")
        
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        if file_size > Config.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        
        # Generate unique file ID and filename
        file_id = str(uuid.uuid4())
        file_extension = Path(file.filename).suffix
        stored_filename = f"{file_id}{file_extension}"
        file_path = Config.UPLOAD_DIR / stored_filename
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Create thumbnail for images
        thumbnail_path = None
        if get_file_type(file.filename) == 'images':
            thumbnail_filename = f"{file_id}_thumb.jpg"
            thumbnail_path = Config.THUMBNAILS_DIR / thumbnail_filename
            create_thumbnail(file_path, thumbnail_path)
        
        # Generate file URL
        file_url = f"{Config.BASE_URL}/files/{file_id}"
        
        # Save metadata
        metadata = {
            "file_id": file_id,
            "original_filename": file.filename,
            "filename": stored_filename,
            "url": file_url,
            "file_size": file_size,
            "upload_time": datetime.now().isoformat(),
            "file_type": get_file_type(file.filename),
            "content_type": file.content_type,
            "has_thumbnail": thumbnail_path is not None
        }
        
        save_file_metadata(file_id, metadata)
        
        logger.info(f"File uploaded: {file.filename} -> {file_id}")
        
        return UploadResponse(
            success=True,
            file_id=file_id,
            url=file_url,
            original_filename=file.filename,
            file_size=file_size,
            message="File uploaded successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/files/{file_id}")
async def get_file(file_id: str):
    """Get a file by ID"""
    try:
        # Load metadata
        metadata = load_file_metadata(file_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check if file exists
        file_path = Config.UPLOAD_DIR / metadata["filename"]
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        # Return file
        return FileResponse(
            path=file_path,
            filename=metadata["original_filename"],
            media_type=metadata.get("content_type", "application/octet-stream")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get file error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/files/{file_id}/info", response_model=FileInfo)
async def get_file_info(file_id: str, auth: bool = Depends(verify_api_key)):
    """Get file information"""
    metadata = load_file_metadata(file_id)
    if not metadata:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileInfo(**metadata)

@app.get("/files/{file_id}/thumbnail")
async def get_thumbnail(file_id: str):
    """Get file thumbnail"""
    try:
        thumbnail_path = Config.THUMBNAILS_DIR / f"{file_id}_thumb.jpg"
        if not thumbnail_path.exists():
            raise HTTPException(status_code=404, detail="Thumbnail not found")
        
        return FileResponse(
            path=thumbnail_path,
            media_type="image/jpeg"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get thumbnail error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/files", response_model=ListFilesResponse)
async def list_files(
    limit: int = 50,
    offset: int = 0,
    auth: bool = Depends(verify_api_key)
):
    """List all files"""
    try:
        all_files = get_all_files()
        
        # Pagination
        total_count = len(all_files)
        files = all_files[offset:offset + limit]
        
        # Convert to FileInfo objects
        file_infos = []
        for file_data in files:
            try:
                file_infos.append(FileInfo(**file_data))
            except Exception as e:
                logger.error(f"Error processing file metadata: {e}")
                continue
        
        return ListFilesResponse(
            files=file_infos,
            total_count=total_count
        )
        
    except Exception as e:
        logger.error(f"List files error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/files/{file_id}", response_model=DeleteResponse)
async def delete_file(file_id: str, auth: bool = Depends(verify_api_key)):
    """Delete a file"""
    try:
        # Load metadata
        metadata = load_file_metadata(file_id)
        if not metadata:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Delete actual file
        file_path = Config.UPLOAD_DIR / metadata["filename"]
        if file_path.exists():
            file_path.unlink()
        
        # Delete thumbnail if exists
        thumbnail_path = Config.THUMBNAILS_DIR / f"{file_id}_thumb.jpg"
        if thumbnail_path.exists():
            thumbnail_path.unlink()
        
        # Delete metadata
        metadata_path = Config.UPLOAD_DIR / f"{file_id}.json"
        if metadata_path.exists():
            metadata_path.unlink()
        
        logger.info(f"File deleted: {file_id}")
        
        return DeleteResponse(
            success=True,
            message="File deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete file error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/files", response_model=DeleteResponse)
async def delete_old_files(
    days: int = 30,
    auth: bool = Depends(verify_api_key)
):
    """Delete files older than specified days"""
    try:
        cutoff_date = datetime.now() - timedelta(days=days)
        deleted_count = 0
        
        all_files = get_all_files()
        
        for file_data in all_files:
            try:
                upload_time = datetime.fromisoformat(file_data["upload_time"])
                
                if upload_time < cutoff_date:
                    # Delete the file
                    await delete_file(file_data["file_id"])
                    deleted_count += 1
                    
            except Exception as e:
                logger.error(f"Error processing file for deletion: {e}")
                continue
        
        return DeleteResponse(
            success=True,
            message=f"Deleted {deleted_count} old files"
        )
        
    except Exception as e:
        logger.error(f"Delete old files error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/stats")
async def get_stats(auth: bool = Depends(verify_api_key)):
    """Get server statistics"""
    try:
        all_files = get_all_files()
        
        total_files = len(all_files)
        total_size = sum(file_data.get("file_size", 0) for file_data in all_files)
        
        # File type breakdown
        type_counts = {}
        for file_data in all_files:
            file_type = file_data.get("file_type", "unknown")
            type_counts[file_type] = type_counts.get(file_type, 0) + 1
        
        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "file_types": type_counts,
            "server_uptime": "Server running"
        }
        
    except Exception as e:
        logger.error(f"Get stats error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Admin Interface Endpoints
@app.get("/client", response_class=HTMLResponse)
async def client_interface(request: Request):
    """Serve the client interface"""
    return templates.TemplateResponse("client.html", {"request": request})

@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login(request: Request):
    """Serve the admin login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Serve the admin dashboard - Admin access only"""
    # In production, add proper admin authentication here
    # For now, we'll serve the dashboard directly
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/admin/files")
async def admin_get_files():
    """Get all files for admin dashboard"""
    try:
        all_files = get_all_files()
        
        # Convert to FileInfo format
        files = []
        for file_data in all_files:
            file_info = FileInfo(
                file_id=file_data["file_id"],
                original_filename=file_data["original_filename"],
                filename=file_data["filename"],
                url=f"{Config.BASE_URL}/files/{file_data['file_id']}",
                file_size=file_data["file_size"],
                upload_time=file_data["upload_time"],
                file_type=file_data["file_type"]
            )
            files.append(file_info)
        
        return {"files": files, "total_count": len(files)}
        
    except Exception as e:
        logger.error(f"Admin get files error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/admin/files/{file_id}")
async def admin_delete_file(file_id: str):
    """Delete a specific file - Admin only"""
    try:
        result = await delete_file(file_id)
        return result
    except Exception as e:
        logger.error(f"Admin delete file error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/admin/stats")
async def admin_get_stats():
    """Get detailed statistics for admin dashboard"""
    try:
        all_files = get_all_files()
        
        total_files = len(all_files)
        total_size = sum(file_data.get("file_size", 0) for file_data in all_files)
        
        # Calculate uploads today
        today = datetime.now().date()
        uploads_today = 0
        
        for file_data in all_files:
            try:
                upload_date = datetime.fromisoformat(file_data["upload_time"]).date()
                if upload_date == today:
                    uploads_today += 1
            except:
                continue
        
        # File type breakdown
        type_counts = {}
        for file_data in all_files:
            file_type = file_data.get("file_type", "unknown")
            category = "other"
            if file_type.startswith("image/"):
                category = "images"
            elif file_type.startswith("video/"):
                category = "videos"
            elif file_type.startswith("audio/"):
                category = "audio"
            elif "pdf" in file_type or "document" in file_type:
                category = "documents"
            
            type_counts[category] = type_counts.get(category, 0) + 1
        
        return {
            "total_files": total_files,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "uploads_today": uploads_today,
            "file_types": type_counts,
            "server_uptime": "Online"
        }
        
    except Exception as e:
        logger.error(f"Admin get stats error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=False
    )
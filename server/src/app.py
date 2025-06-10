#!/usr/bin/env python3
"""
Custom Server File Manager - Server Application
A FastAPI-based file server designed for Railway deployment
"""

import os
import uuid
import json
import time
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
    @classmethod
    def get_base_url(cls):
        """Get BASE_URL dynamically based on current environment"""
        # Get the actual port being used
        current_port = cls.PORT
        default_local_url = f"http://localhost:{current_port}"
        
        raw_base_url = os.getenv("RAILWAY_PUBLIC_DOMAIN", 
                                 os.getenv("RAILWAY_STATIC_URL", 
                                          os.getenv("PUBLIC_URL", default_local_url)))
        
        # Ensure protocol is included
        if raw_base_url.startswith("http://") or raw_base_url.startswith("https://"):
            final_url = raw_base_url
        else:
            # For Railway deployment, use https:// for domains without protocol
            if "localhost" in raw_base_url or "127.0.0.1" in raw_base_url:
                final_url = f"http://{raw_base_url}"
            else:
                final_url = f"https://{raw_base_url}"
        
        # Debug logging
        logger.info(f"BASE_URL configuration: PORT={current_port}, RAW={raw_base_url}, FINAL={final_url}")
        return final_url

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
security = HTTPBearer(auto_error=False)

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key - optional in development mode"""
    # If no API key is provided and we're in development mode, allow access
    if credentials is None:
        # Check if we're in development mode (localhost)
        if "localhost" in Config.get_base_url() or "127.0.0.1" in Config.get_base_url():
            return True
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required for production access"
            )
    
    # If API key is provided, verify it
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

# Performance optimization: Add caching
_file_cache = {}
_cache_timestamp = 0
_stats_cache = {}
_stats_cache_timestamp = 0
CACHE_TTL = 30  # Cache for 30 seconds
STATS_CACHE_TTL = 15  # Stats cache for 15 seconds (faster refresh for UI)

def get_all_files() -> List[Dict[str, Any]]:
    """Get all file metadata with caching and performance optimizations"""
    global _file_cache, _cache_timestamp
    current_time = time.time()
    
    # Check if cache is still valid
    if current_time - _cache_timestamp < CACHE_TTL and _file_cache:
        return _file_cache.get('files', [])
    
    files = []
    try:
        # Use pathlib for faster file operations
        json_files = list(Config.UPLOAD_DIR.glob("*.json"))
        
        # Early return if no files
        if not json_files:
            _file_cache = {'files': []}
            _cache_timestamp = current_time
            return []
        
        # Process files with better error handling and performance
        for json_file in json_files:
            try:
                # Check file size before reading (skip very large metadata files)
                if json_file.stat().st_size > 10240:  # Skip files > 10KB (unusual for metadata)
                    logger.warning(f"Skipping unusually large metadata file: {json_file}")
                    continue
                    
                with open(json_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    
                    # Validate metadata structure
                    if 'file_id' in metadata and 'upload_time' in metadata:
                        files.append(metadata)
                    else:
                        logger.warning(f"Invalid metadata structure in {json_file}")
                        
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.error(f"Error reading metadata file {json_file}: {e}")
                continue
            except Exception as e:
                logger.error(f"Unexpected error reading metadata file {json_file}: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Error scanning files directory: {e}")
        return []
    
    # Sort by upload time (newest first) - optimized key function
    try:
        files.sort(key=lambda x: x.get('upload_time', '1970-01-01T00:00:00'), reverse=True)
    except Exception as e:
        logger.error(f"Error sorting files: {e}")
        # Fallback to unsorted list
    
    # Update cache
    _file_cache = {'files': files}
    _cache_timestamp = current_time
    
    logger.debug(f"Loaded {len(files)} files in {time.time() - current_time:.3f}s")
    
    return files

def invalidate_file_cache():
    """Invalidate the file cache to force refresh"""
    global _file_cache, _cache_timestamp, _stats_cache, _stats_cache_timestamp
    _file_cache = {}
    _cache_timestamp = 0
    _stats_cache = {}
    _stats_cache_timestamp = 0

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

def resize_image_if_needed(image_path: Path, max_resolution: int = 2048, quality: int = 85):
    """Resize image if it exceeds maximum resolution while maintaining aspect ratio"""
    try:
        with Image.open(image_path) as img:
            # Get original dimensions
            original_width, original_height = img.size
            
            # Check if resizing is needed
            if original_width <= max_resolution and original_height <= max_resolution:
                logger.info(f"Image {image_path.name} ({original_width}x{original_height}) is within size limits, no resize needed")
                return False  # No resize needed
            
            # Calculate new dimensions maintaining aspect ratio
            if original_width > original_height:
                # Landscape or square
                new_width = max_resolution
                new_height = int((original_height * max_resolution) / original_width)
            else:
                # Portrait
                new_height = max_resolution
                new_width = int((original_width * max_resolution) / original_height)
            
            # Resize the image
            resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save with optimization
            # Preserve original format if possible, fallback to JPEG for better compression
            if img.format in ['JPEG', 'JPG']:
                resized_img.save(image_path, format='JPEG', optimize=True, quality=quality)
            elif img.format == 'PNG':
                # For PNG, check if it has transparency
                if resized_img.mode in ('RGBA', 'LA') or (resized_img.mode == 'P' and 'transparency' in resized_img.info):
                    resized_img.save(image_path, format='PNG', optimize=True)
                else:
                    # Convert to JPEG for better compression if no transparency
                    rgb_img = Image.new('RGB', resized_img.size, (255, 255, 255))
                    rgb_img.paste(resized_img, mask=resized_img.split()[-1] if resized_img.mode == 'RGBA' else None)
                    rgb_img.save(image_path, format='JPEG', optimize=True, quality=quality)
            else:
                # For other formats, convert to JPEG
                rgb_img = resized_img.convert('RGB')
                rgb_img.save(image_path, format='JPEG', optimize=True, quality=quality)
            
            logger.info(f"Image {image_path.name} resized from {original_width}x{original_height} to {new_width}x{new_height}")
            return True  # Resize was performed
            
    except Exception as e:
        logger.error(f"Error resizing image {image_path}: {e}")
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
        
        # Ensure files subdirectory exists
        files_dir = Config.UPLOAD_DIR / "files"
        files_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = files_dir / stored_filename
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Auto-resize images if they're too large (before creating thumbnail)
        resized = False
        if get_file_type(file.filename) == 'images':
            resized = resize_image_if_needed(file_path, max_resolution=2048, quality=85)
            # Update file size if image was resized
            if resized:
                file_size = file_path.stat().st_size
        
        # Create thumbnail for images
        thumbnail_path = None
        if get_file_type(file.filename) == 'images':
            thumbnail_filename = f"{file_id}_thumb.jpg"
            thumbnail_path = Config.THUMBNAILS_DIR / thumbnail_filename
            create_thumbnail(file_path, thumbnail_path)
        
        # Generate file URL with proper extension for direct image viewing
        file_extension = Path(file.filename).suffix.lower()
        if get_file_type(file.filename) == 'images':
            # For images, use direct file serving with extension
            file_url = f"{Config.get_base_url()}/files/{file_id}{file_extension}"
        else:
            # For other files, use standard endpoint
            file_url = f"{Config.get_base_url()}/files/{file_id}"
        
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
            "has_thumbnail": thumbnail_path is not None,
            "was_resized": resized
        }
        
        save_file_metadata(file_id, metadata)
        
        # Invalidate file cache to ensure fresh data on next request
        invalidate_file_cache()
        
        # Log upload with resize information
        resize_info = " (auto-resized)" if resized else ""
        logger.info(f"File uploaded: {file.filename} -> {file_id}{resize_info}")
        
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
    """Get a file by ID - handles both with and without extensions"""
    try:
        # Parse file_id and extension if present
        actual_file_id = file_id
        extension = None
        
        if '.' in file_id:
            # Has extension - extract file_id and extension
            actual_file_id, ext = file_id.rsplit('.', 1)
            extension = f".{ext}"
        
        # Load metadata
        metadata = load_file_metadata(actual_file_id)
        if not metadata:
            raise HTTPException(status_code=404, detail=f"File metadata not found for ID: {actual_file_id}")
        
        # Get filename from metadata
        filename = metadata.get("filename")
        if not filename:
            raise HTTPException(status_code=404, detail="File metadata incomplete - no filename")
            
        # Try to find the file in the correct location
        # New files are stored in uploads/files/
        file_path = Config.UPLOAD_DIR / "files" / filename
        
        if not file_path.exists():
            # Fallback: try the root upload directory for older files
            file_path = Config.UPLOAD_DIR / filename
            
        if not file_path.exists():
            # Debug logging to understand what's happening
            logger.error(f"File not found: {filename}")
            logger.error(f"Checked paths:")
            logger.error(f"  - {Config.UPLOAD_DIR / 'files' / filename}")
            logger.error(f"  - {Config.UPLOAD_DIR / filename}")
            logger.error(f"Upload dir contents: {list(Config.UPLOAD_DIR.iterdir()) if Config.UPLOAD_DIR.exists() else 'Directory does not exist'}")
            files_dir = Config.UPLOAD_DIR / "files"
            logger.error(f"Files dir contents: {list(files_dir.iterdir()) if files_dir.exists() else 'Directory does not exist'}")
            raise HTTPException(status_code=404, detail=f"File not found on disk: {filename}")
        
        # Determine content type and display behavior
        content_type = metadata.get("content_type", "application/octet-stream")
        original_filename = metadata.get("original_filename", filename)
        
        # Enhanced image serving logic for better browser compatibility
        if extension and get_file_type(original_filename) == 'images':
            # For images accessed with extension, serve inline with proper headers
            headers = {
                "Content-Disposition": "inline",
                "Cache-Control": "public, max-age=3600",  # Cache for 1 hour
                "Cross-Origin-Resource-Policy": "cross-origin"  # Allow cross-origin access
            }
            return FileResponse(
                path=file_path,
                media_type=content_type,
                headers=headers
            )
        else:
            # Standard download behavior for non-images or access without extension
            return FileResponse(
                path=file_path,
                filename=original_filename,
                media_type=content_type
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get file error for {file_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

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
        
        # Delete actual file - handle both old and new metadata formats
        filename = metadata.get("filename", metadata.get("stored_filename"))
        if filename:
            file_path = Config.UPLOAD_DIR / "files" / filename
            if not file_path.exists():
                # Try in the root upload directory for older files
                file_path = Config.UPLOAD_DIR / filename
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
        
        # Invalidate file cache to ensure fresh data on next request
        invalidate_file_cache()
        
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
        
        # Invalidate file cache once after all deletions
        if deleted_count > 0:
            invalidate_file_cache()
        
        return DeleteResponse(
            success=True,
            message=f"Deleted {deleted_count} old files"
        )
        
    except Exception as e:
        logger.error(f"Delete old files error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/stats")
async def get_stats(auth: bool = Depends(verify_api_key)):
    """Get server statistics with caching for better performance"""
    global _stats_cache, _stats_cache_timestamp
    current_time = time.time()
    
    # Check if stats cache is still valid
    if current_time - _stats_cache_timestamp < STATS_CACHE_TTL and _stats_cache:
        return _stats_cache
    
    try:
        all_files = get_all_files()
        
        if not all_files:
            # Handle empty file list case
            stats = {
                "total_files": 0,
                "total_size_bytes": 0,
                "total_size_mb": 0.0,
                "file_types": {},
                "server_uptime": "Server running"
            }
        else:
            # Optimized single-pass calculation
            total_files = len(all_files)
            total_size = 0
            type_counts = {}
            
            for file_data in all_files:
                # Size calculation
                file_size = file_data.get("file_size", 0)
                if isinstance(file_size, (int, float)):
                    total_size += file_size
                
                # Type counting
                file_type = file_data.get("file_type", "unknown")
                type_counts[file_type] = type_counts.get(file_type, 0) + 1
            
            stats = {
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2) if total_size > 0 else 0.0,
                "file_types": type_counts,
                "server_uptime": "Server running"
            }
        
        # Update stats cache
        _stats_cache = stats
        _stats_cache_timestamp = current_time
        
        return stats
        
    except Exception as e:
        logger.error(f"Get stats error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Admin Interface Endpoints
@app.get("/client", response_class=HTMLResponse)
async def client_interface(request: Request):
    """Serve the client interface"""
    return templates.TemplateResponse("client_working.html", {"request": request})

@app.get("/debug", response_class=HTMLResponse)
async def debug_interface(request: Request):
    """Serve the debug test page for UI troubleshooting"""
    return templates.TemplateResponse("debug.html", {"request": request})

@app.get("/simple-test", response_class=HTMLResponse)
async def simple_test_interface(request: Request):
    """Serve a simple UI interaction test page"""
    return templates.TemplateResponse("simple_test.html", {"request": request})

@app.get("/client-test", response_class=HTMLResponse)
async def client_test_interface(request: Request):
    """Serve a client interface test page"""
    return templates.TemplateResponse("client_test.html", {"request": request})

@app.get("/client-working", response_class=HTMLResponse)
async def client_working_interface(request: Request):
    """Serve a working client interface with inline JavaScript"""
    return templates.TemplateResponse("client_working.html", {"request": request})

@app.get("/client-original", response_class=HTMLResponse)
async def client_original_interface(request: Request):
    """Serve the original client interface (for comparison/debugging)"""
    return templates.TemplateResponse("client.html", {"request": request})

@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login(request: Request):
    """Serve the admin login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Serve the admin dashboard - Admin access only"""
    # Serve the working admin interface with fixed UI interactions
    return templates.TemplateResponse("admin_working.html", {"request": request})

@app.get("/admin/enhanced", response_class=HTMLResponse)
async def admin_enhanced_dashboard(request: Request):
    """Serve the enhanced admin dashboard with advanced features"""
    return templates.TemplateResponse("admin_enhanced.html", {"request": request})

@app.get("/admin-original", response_class=HTMLResponse)
async def admin_original_dashboard(request: Request):
    """Serve the original admin dashboard (for comparison/debugging)"""
    return templates.TemplateResponse("admin.html", {"request": request})

@app.get("/admin-comparison", response_class=HTMLResponse)
async def admin_comparison(request: Request):
    """Show comparison between broken and working admin interfaces"""
    return templates.TemplateResponse("admin_comparison.html", {"request": request})

@app.get("/admin/files")
async def admin_get_files():
    """Get all files for admin dashboard"""
    try:
        all_files = get_all_files()
        
        # Convert to FileInfo format with proper URLs
        files = []
        for file_data in all_files:
            # Generate proper URL with extension for images
            file_id = file_data["file_id"]
            file_extension = Path(file_data["original_filename"]).suffix
            
            if get_file_type(file_data["original_filename"]) == 'images':
                url = f"{Config.get_base_url()}/files/{file_id}{file_extension}"
            else:
                url = f"{Config.get_base_url()}/files/{file_id}"
            
            # Check if thumbnail exists
            thumbnail_path = Config.THUMBNAILS_DIR / f"{file_id}_thumb.jpg"
            has_thumbnail = thumbnail_path.exists()
            thumbnail_url = f"{Config.get_base_url()}/files/{file_id}/thumbnail" if has_thumbnail else None
            
            file_info = FileInfo(
                file_id=file_data["file_id"],
                original_filename=file_data["original_filename"],
                filename=file_data["filename"],
                url=url,
                file_size=file_data["file_size"],
                upload_time=file_data["upload_time"],
                file_type=file_data["file_type"]
            )
            
            # Add thumbnail info (convert to dict to add extra fields)
            file_dict = file_info.dict()
            file_dict["thumbnail_url"] = thumbnail_url
            file_dict["has_thumbnail"] = has_thumbnail
            files.append(file_dict)
        
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
    """Get detailed statistics for admin dashboard with caching"""
    global _stats_cache, _stats_cache_timestamp
    current_time = time.time()
    
    # Check if detailed stats cache exists and is valid
    admin_cache_key = 'admin_stats'
    if (current_time - _stats_cache_timestamp < STATS_CACHE_TTL and 
        _stats_cache and admin_cache_key in _stats_cache):
        return _stats_cache[admin_cache_key]
    
    try:
        all_files = get_all_files()
        
        if not all_files:
            # Handle empty file list case
            admin_stats = {
                "total_files": 0,
                "total_size_bytes": 0,
                "total_size_mb": 0.0,
                "uploads_today": 0,
                "file_types": {},
                "server_uptime": "Online"
            }
        else:
            total_files = len(all_files)
            total_size = 0
            uploads_today = 0
            type_counts = {}
            today = datetime.now().date()
            
            # Single-pass optimization
            for file_data in all_files:
                # Size calculation
                file_size = file_data.get("file_size", 0)
                if isinstance(file_size, (int, float)):
                    total_size += file_size
                
                # Uploads today calculation
                try:
                    upload_time = file_data.get("upload_time")
                    if upload_time:
                        upload_date = datetime.fromisoformat(upload_time).date()
                        if upload_date == today:
                            uploads_today += 1
                except Exception:
                    pass  # Skip invalid dates
                
                # File type categorization
                file_type = file_data.get("file_type", "unknown")
                category = "other"
                if isinstance(file_type, str):
                    if file_type.startswith("image/"):
                        category = "images"
                    elif file_type.startswith("video/"):
                        category = "videos"
                    elif file_type.startswith("audio/"):
                        category = "audio"
                    elif "pdf" in file_type or "document" in file_type:
                        category = "documents"
                
                type_counts[category] = type_counts.get(category, 0) + 1
            
            admin_stats = {
                "total_files": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2) if total_size > 0 else 0.0,
                "uploads_today": uploads_today,
                "file_types": type_counts,
                "server_uptime": "Online"
            }
        
        # Update admin stats cache
        if not _stats_cache:
            _stats_cache = {}
        _stats_cache[admin_cache_key] = admin_stats
        _stats_cache_timestamp = current_time
        
        return admin_stats
        
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
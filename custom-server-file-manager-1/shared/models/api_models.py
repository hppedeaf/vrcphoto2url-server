from pydantic import BaseModel
from typing import List, Optional

class FileModel(BaseModel):
    id: str
    name: str
    size: int
    upload_time: str
    file_type: str
    url: str

class UploadResponse(BaseModel):
    success: bool
    message: str
    file: Optional[FileModel]

class FileListResponse(BaseModel):
    success: bool
    files: List[FileModel]

class ErrorResponse(BaseModel):
    success: bool
    error: str
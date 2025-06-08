from typing import List, Dict

class FileService:
    """Service for handling file operations."""

    def __init__(self, storage_service):
        self.storage_service = storage_service

    def upload_file(self, file_data: bytes, filename: str) -> str:
        """Upload a file to the storage service."""
        file_url = self.storage_service.save_file(file_data, filename)
        return file_url

    def delete_file(self, file_id: str) -> bool:
        """Delete a file from the storage service."""
        return self.storage_service.remove_file(file_id)

    def list_files(self) -> List[Dict]:
        """List all files stored in the storage service."""
        return self.storage_service.get_all_files()

    def get_file(self, file_id: str) -> bytes:
        """Retrieve a file from the storage service."""
        return self.storage_service.fetch_file(file_id)
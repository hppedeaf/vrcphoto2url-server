class FileModel:
    """Data model for files in the server application."""
    
    def __init__(self, filename: str, file_size: int, upload_time: str, file_id: str):
        self.filename = filename
        self.file_size = file_size
        self.upload_time = upload_time
        self.file_id = file_id

    def to_dict(self):
        """Convert the file model to a dictionary representation."""
        return {
            'filename': self.filename,
            'file_size': self.file_size,
            'upload_time': self.upload_time,
            'file_id': self.file_id
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Create a FileModel instance from a dictionary."""
        return cls(
            filename=data.get('filename'),
            file_size=data.get('file_size'),
            upload_time=data.get('upload_time'),
            file_id=data.get('file_id')
        )
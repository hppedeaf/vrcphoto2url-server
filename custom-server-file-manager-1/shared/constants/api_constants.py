# File: /custom-server-file-manager/shared/constants/api_constants.py

BASE_API_URL = "https://api.example.com/v1"
TIMEOUT = 30  # seconds
MAX_UPLOAD_SIZE = 10485760  # 10 MB
SUPPORTED_FILE_TYPES = ['image/jpeg', 'image/png', 'application/pdf']
ERROR_MESSAGES = {
    'file_too_large': "The uploaded file exceeds the maximum allowed size.",
    'unsupported_file_type': "The uploaded file type is not supported.",
    'upload_failed': "File upload failed. Please try again.",
    'server_error': "An error occurred on the server. Please try again later."
}
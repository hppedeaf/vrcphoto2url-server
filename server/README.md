# Custom File Server - FastAPI Backend

A modern, scalable file server built with FastAPI, designed for deployment on Railway.com. This server provides secure file upload, download, and management capabilities with API key authentication.

## Features

- **FastAPI Framework**: Modern, high-performance web framework with automatic API documentation
- **File Management**: Upload, download, list, and delete files with metadata storage
- **Authentication**: API key-based authentication for secure access
- **Thumbnail Generation**: Automatic thumbnail creation for supported image formats
- **Storage Monitoring**: Real-time storage usage and statistics
- **Railway Deployment**: Pre-configured for easy deployment on Railway.com
- **JSON Metadata**: File information stored as JSON with upload timestamps and metadata
- **Health Monitoring**: Built-in health check and server status endpoints

## Project Structure

```
server/
├── src/
## Installation

### Local Development

1. **Navigate to the server directory**:
   ```powershell
   cd custom-server-file-manager-1\server
   ```

2. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```powershell
   copy .env.example .env
   # Edit .env with your preferred settings
   ```

4. **Run the server locally**:
   ```powershell
   uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
   ```

The server will be available at `http://localhost:8000`

### Railway.com Deployment

1. **Create a Railway account** at [railway.app](https://railway.app)

2. **Connect your repository** to Railway

3. **Set environment variables** in Railway dashboard:
   - `API_KEY`: Your chosen API key for authentication
   - `ENVIRONMENT`: `production`
   - `MAX_FILE_SIZE_MB`: Maximum file size (default: 50)

4. **Deploy**: Railway will automatically deploy using the `Procfile` configuration

## Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Server Configuration
API_KEY=your-secret-api-key-here
ENVIRONMENT=development
MAX_FILE_SIZE_MB=50
UPLOAD_FOLDER=uploads
THUMBNAILS_FOLDER=thumbnails

# Railway-specific (auto-configured)
PORT=8000
```

## API Endpoints

### Authentication
All endpoints (except `/health`) require the `Authorization: Bearer <API_KEY>` header.

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Server health check |
| `GET` | `/stats` | Server statistics and storage info |
| `POST` | `/upload` | Upload a new file |
| `GET` | `/files` | List all uploaded files |
| `GET` | `/files/{file_id}` | Download specific file |
| `DELETE` | `/files/{file_id}` | Delete specific file |

### API Documentation

Once running, visit:
- **Interactive docs**: `http://localhost:8000/docs` (Swagger UI)
- **Alternative docs**: `http://localhost:8000/redoc` (ReDoc)

### Example Usage

**Upload a file**:
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Authorization: Bearer your-api-key" \
  -F "file=@example.png"
```

**List files**:
```bash
curl -X GET "http://localhost:8000/files" \
  -H "Authorization: Bearer your-api-key"
```

**Download file**:
```bash
curl -X GET "http://localhost:8000/files/{file_id}" \
  -H "Authorization: Bearer your-api-key" \
  --output downloaded_file.png
```

## Storage Structure

```
uploads/
├── files/
│   ├── {uuid}.{extension}     # Original uploaded files
│   └── {uuid}.json           # File metadata
└── thumbnails/
    └── {uuid}_thumb.{ext}    # Generated thumbnails
```

## Features

### File Upload
- Multi-format support (images, documents, etc.)
- Automatic UUID generation for unique file identification
- Metadata storage (filename, size, upload date, content type)
- File size validation

### Thumbnail Generation
- Automatic thumbnail creation for supported image formats
- Configurable thumbnail size (default: 200x200px)
- Maintains aspect ratio with proper scaling

### Storage Management
- Real-time storage usage monitoring
- File size tracking and reporting
- Configurable maximum file size limits

## Security

- **API Key Authentication**: All endpoints require valid API key
- **File Type Validation**: Configurable allowed file types
- **Size Limits**: Configurable maximum file size
- **UUID File Names**: Prevents path traversal and conflicts

## Monitoring

### Health Check
`GET /health` provides server status without authentication.

### Statistics
`GET /stats` provides:
- Total files count
- Total storage usage
- Available disk space
- Server uptime
- Version information

## Troubleshooting

### Common Issues

**Port already in use**:
```powershell
# Change port in command
uvicorn src.app:app --reload --port 8001
```

**Permission errors**:
```powershell
# Ensure write permissions for upload directories
mkdir uploads
mkdir uploads\files
mkdir uploads\thumbnails
```

**Module import errors**:
```powershell
# Ensure you're in the server directory
cd server
python -m pip install --upgrade -r requirements.txt
```

### Railway Deployment Issues

1. **Check Railway logs** for deployment errors
2. **Verify environment variables** are set correctly
3. **Ensure Procfile** is correctly configured
4. **Check file paths** are relative to project root

## Development

### Adding New Endpoints

Add new routes to `src/app.py`:

```python
@app.get("/new-endpoint")
async def new_endpoint():
    return {"message": "Hello World"}
```

### Database Integration

To add database support, consider integrating:
- **SQLAlchemy** for ORM
- **Alembic** for migrations
- **PostgreSQL** or **SQLite** for storage

## License

This project is open source. See the main project documentation for license information.
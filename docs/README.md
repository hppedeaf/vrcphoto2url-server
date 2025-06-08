# Custom File Server Client

A modern desktop GUI client for connecting to and managing files on a custom FastAPI-based file server. This client application provides a user-friendly interface for uploading, downloading, and managing files remotely.

## Features

- **Server Connection**: Connect to any compatible file server with URL and API key authentication
- **File Upload**: Upload files to the server with progress tracking and real-time feedback
- **File Management**: View, download, and delete files on the server with detailed file information
- **Real-time Updates**: Auto-refresh file list and server statistics every 30 seconds
- **User-friendly Interface**: Modern GUI built with PySide6 featuring resizable panels and intuitive controls
- **Connection Testing**: Built-in connection testing to verify server accessibility before connecting
- **URL Copying**: Copy direct file URLs to clipboard for easy sharing
- **Server Statistics**: Real-time display of server storage usage and file counts

## Installation

### Prerequisites

- Python 3.8 or higher
- Windows, macOS, or Linux

### Installation Steps

1. **Navigate to the client directory**:
   ```powershell
   cd custom-server-file-manager-1\client
   ```

2. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

## Usage

### Running the Client

**Option 1 - Using the run script (Recommended)**:
```powershell
python run_client.py
```

**Option 2 - From the src directory**:
```powershell
cd src
python custom_main.py
```

### Connecting to a Server

1. **Launch the application** and click "Connect to Server"
2. **Enter server details**:
   - Server URL: `https://your-server.railway.app` (or your server's URL)
   - API Key: Your server's authentication key (if required)
3. **Test the connection** by clicking "Test Connection"
4. **Connect** by clicking "Connect" once the test succeeds

### File Operations

- **Upload Files**: Click "Upload File" or use File → Upload to select and upload files
- **View Files**: Connected files appear in the right panel with size information
- **Download Files**: Double-click any file or select it and click "Download Selected"
- **Copy URLs**: Select a file and click "Copy URL" to copy the direct file URL
- **Delete Files**: Select a file and click "Delete Selected" (with confirmation)
- **Auto-refresh**: File list updates automatically every 30 seconds

## Server Compatibility

This client is designed to work with the FastAPI-based file server that provides these endpoints:

- `GET /health` - Server health check
- `GET /stats` - Server statistics and storage info
- `POST /upload` - File upload with multipart/form-data
- `GET /files` - List all uploaded files
- `GET /files/{file_id}` - Download specific file
- `DELETE /files/{file_id}` - Delete specific file

## Configuration

The application automatically saves your last connection settings. No manual configuration file editing is required.

## Troubleshooting

### Connection Issues

1. **Invalid URL**: Ensure the server URL includes `https://` or `http://`
2. **API Key**: Verify your API key is correct (check server configuration)
3. **Network**: Ensure internet connectivity and server accessibility
4. **Server Status**: Verify the server is running and responding

### Installation Issues

**Missing dependencies**:
```powershell
pip install --upgrade -r requirements.txt
```

**PySide6 issues on Linux**:
```bash
sudo apt-get install python3-pyside6
```

### Runtime Issues

**Import errors**: Ensure you're running from the correct directory and all dependencies are installed.

**GUI not appearing**: Check that your system supports GUI applications and PySide6 is properly installed.

## Development

### Project Structure

```
client/
├── run_client.py           # Main entry point (recommended)
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── src/
    ├── custom_main.py          # Alternative entry point
    ├── custom_server_client.py # Server communication logic
    ├── custom_server_dialog.py # Connection dialog
    └── ui/
        └── main_window.py      # Main application window
```

### Adding Features

The codebase is modular and easy to extend:

- **Server communication**: Modify `custom_server_client.py`
- **UI components**: Edit files in `src/ui/`
- **Connection logic**: Update `custom_server_dialog.py`

## License

This project is open source. See the main project documentation for license information.
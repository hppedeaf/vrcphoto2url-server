# Custom Server File Manager - Modern Desktop Client

A beautiful, modern desktop client application for the Custom Server File Manager. This standalone desktop application provides an intuitive interface for file uploads, monitoring, and server management with a sleek dark theme design.

![Desktop Client](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue) ![Python](https://img.shields.io/badge/Python-3.8%2B-green) ![GUI](https://img.shields.io/badge/GUI-PySide6-orange)

## ✨ Features

### 🎨 Modern Design
- **Beautiful Dark Theme**: Sleek dark interface with customizable green accent colors
- **Modern UI Components**: Custom-designed cards, buttons, and status indicators
- **Responsive Layout**: Adaptive interface that works on different screen sizes
- **Visual Feedback**: Progress bars, notifications, and real-time status updates

### 📁 File Management
- **Drag & Drop Upload**: Simply drag files to the upload zone for instant uploads
- **Multi-file Selection**: Upload multiple files simultaneously with batch processing
- **Upload Queue**: Organized queue with individual progress tracking
- **File Type Support**: Images, videos, audio, documents, and archives
- **Smart Previews**: Thumbnail generation and file type detection

### 🔄 Auto-Upload & Monitoring
- **Folder Monitoring**: Automatically watch folders for new files (requires watchdog)
- **Auto-Upload**: Instantly upload new files when detected in monitored folders
- **Clipboard Integration**: Monitor clipboard for new images and auto-upload
- **Smart Filtering**: Configure which file types to upload automatically

### 📊 Activity Tracking
- **Upload History**: Complete log of all upload activities with timestamps
- **File Browser**: View and manage uploaded files with detailed information
- **Statistics**: Track upload counts, data usage, and success rates
- **Real-time Updates**: Live activity feed with server communication status

### ⚙️ Advanced Settings
- **Server Configuration**: Easy server connection setup with testing
- **Upload Preferences**: Customize upload behavior and file handling
- **Theme Options**: Multiple color presets (Green, Blue, Purple, Orange) and customization
- **Notification Settings**: Control when and how to receive notifications

## 🚀 Quick Start

### Prerequisites
- **Python 3.8+**: Make sure Python is installed on your system
- **Operating System**: Windows 10/11 (optimized), macOS, or Linux

### Installation

1. **Navigate to the client directory**:
   ```powershell
   cd custom-server-file-manager-1\client
   ```

2. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

### Running the Client

**Option 1: Windows Batch File (Recommended for Windows)**
```powershell
start_client.bat
```

**Option 2: Python Run Script (Cross-platform)**
```powershell
python run_client.py
```

**Option 3: Main Entry Point**
```powershell
python main.py
```

**Option 4: Test Before Running**
```powershell
python test_client.py
```

## 🔧 Configuration

### First Time Setup

1. **Launch the Client**: Use any of the methods above
2. **Configure Server Connection**:
   - Click "Connect to Server" in the header
   - Enter your server URL (e.g., `https://your-server.railway.app`)
   - Enter your API key (if authentication is enabled)
   - Click "Test Connection" to verify
   - Click "Connect" to establish connection

3. **Set Upload Preferences**:
   - Click the Settings (⚙️) icon in the header
   - Navigate through the tabs to configure:
     - **General**: Auto-upload and notification settings
     - **Upload**: File types, image processing, monitoring folders
     - **Theme**: Color schemes and interface customization
     - **Advanced**: Network settings and debug options

### Server Requirements

The client connects to a Custom Server File Manager server. Ensure you have:
- **Server URL**: Complete URL including protocol (e.g., `https://your-server.com`)
- **API Key**: Valid authentication key (if server requires it)
- **Network Access**: Client must be able to reach the server

## 📱 User Interface Guide

### Header Section
- **🔗 Connection Status**: Green indicator when connected to server
- **📊 Upload Counter**: Shows total files uploaded in current session
- **⚙️ Settings Button**: Access all configuration options
- **🔌 Connect Button**: Set up or change server connection

### Main Content Area

**Left Panel - Upload Zone**
- **📂 Drag & Drop Zone**: Drop files here for instant upload
- **Browse Files**: Click to select files manually
- **📋 Upload Queue**: Shows pending, active, and completed uploads with progress

**Right Panel - Activity Tabs**
- **📝 Activity Log**: Real-time upload history with timestamps and status
- **📁 Files Tab**: Browse and manage uploaded files with download/delete options
- **📈 Statistics**: View upload metrics, success rates, and data usage

### Settings Dialog Tabs

**🏠 General Tab**
- Auto-upload enabled/disabled
- Notification preferences
- Application startup behavior
- Language and region settings

**⬆️ Upload Tab**
- File type filters and restrictions
- Image processing options (resize, quality)
- Upload behavior and retry settings
- Folder monitoring configuration

**🎨 Theme Tab**
- Color presets: Green (default), Blue, Purple, Orange
- Custom color selection with color picker
- Dark/Light theme toggle
- Interface scaling options

**🔧 Advanced Tab**
- Network timeout and retry settings
- Debug logging enabled/disabled
- Performance tuning options
- Cache and temporary file management

## 🛠️ Troubleshooting

### Installation Issues

**Missing Dependencies**
```powershell
pip install PySide6 requests watchdog Pillow pyperclip
```

**Python Version Issues**
- Ensure Python 3.8 or higher is installed
- Check with: `python --version`

### Runtime Issues

**Import Errors**
```powershell
# Run the test script to diagnose issues
python test_client.py
```

**Connection Problems**
- ✅ Verify server URL format (include `https://` or `http://`)
- ✅ Check API key validity
- ✅ Ensure server is running and accessible
- ✅ Test network connectivity
- ✅ Check firewall settings

**File Upload Failures**
- ✅ Verify file permissions
- ✅ Check supported file types
- ✅ Ensure sufficient disk space on server
- ✅ Confirm stable network connection

**GUI Not Starting**
- ✅ Ensure display is available (for remote systems)
- ✅ Check PySide6 installation
- ✅ Verify system GUI support

### Debug Information

**Run with Debug Output**
```powershell
python -c "import sys; sys.path.insert(0, 'src'); from modern_client import ModernCustomClient; print('Debug: Client can be imported')"
```

**Check Component Status**
```powershell
python test_client.py
```

## 📋 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| PySide6 | ≥6.5.0 | GUI framework and Qt bindings |
| requests | ≥2.31.0 | HTTP client for server communication |
| watchdog | ≥3.0.0 | File system monitoring (optional) |
| Pillow | ≥10.0.0 | Image processing and thumbnails |
| pyperclip | ≥1.8.2 | Clipboard integration |

## 🔄 Updates and Maintenance

### Updating Dependencies
```powershell
pip install -r requirements.txt --upgrade
```

### Configuration Backup
Settings are automatically saved to:
- **Windows**: `%APPDATA%\Custom File Manager\`
- **macOS**: `~/Library/Application Support/Custom File Manager/`
- **Linux**: `~/.config/Custom File Manager/`

Configuration files:
- `config.json` - Server connection settings
- `settings.json` - Application preferences
- `activity.log` - Upload history and debug logs

### Resetting Settings
To reset to defaults, delete the configuration directory and restart the application.

## 🏗️ Architecture

### Project Structure
```
client/
├── main.py                 # Main entry point (updated for modern client)
├── run_client.py          # Alternative entry point with error handling
├── start_client.bat       # Windows batch launcher
├── test_client.py         # Component testing script
├── requirements.txt       # Python dependencies
└── src/
    ├── __init__.py            # Package initialization
    ├── modern_client.py       # Main modern desktop client application
    ├── ui_components.py       # Reusable UI components library
    ├── server_client.py       # Server communication manager
    ├── settings_dialog.py     # Settings interface with tabs
    ├── connection_dialog.py   # Server connection configuration
    └── [legacy files...]      # Previous client implementation
```

### Key Components

**ModernCustomClient** (`modern_client.py`)
- Main application window with modern design
- Handles file uploads, monitoring, and user interactions
- Manages application state and settings

**UI Components** (`ui_components.py`)
- ModernCard: Reusable card containers
- ActionButton: Styled buttons with multiple types
- StatusIndicator: Connection and status displays
- FileDropZone: Drag and drop file handling
- NotificationCard: Toast-style notifications

**ServerManager** (`server_client.py`)
- HTTP client for API communication
- File upload with progress tracking
- Error handling and retry logic

## 🤝 Support

If you encounter issues:

1. **Run Diagnostics**: `python test_client.py`
2. **Check Server**: Verify server is running and accessible
3. **Review Logs**: Check console output and application logs
4. **Update Dependencies**: `pip install -r requirements.txt --upgrade`
5. **Reset Settings**: Delete configuration directory if needed

## 📄 Version Information

**Custom Server File Manager Desktop Client**
- Version: 2.0.0
- Build: Modern Desktop Client
- Framework: PySide6 (Qt6)
- Python: 3.8+ required

---

*For server setup and API documentation, see the server directory README.*

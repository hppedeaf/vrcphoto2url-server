# VRCPhoto2URL - VRChat Screenshot to URL Desktop Client

A modern desktop application for uploading VRChat screenshots to a custom server and generating shareable URLs with one-click copy functionality.

## 🎯 Features

### ✨ Desktop Client
- **Modern UI**: Clean, dark-themed interface with red accent colors
- **Drag & Drop Upload**: Simply drag files to upload instantly
- **One-Click URL Copy**: Automatically copies shareable URLs to clipboard
- **File Management**: View, download, and manage uploaded files
- **Activity Tracking**: Real-time upload progress and history
- **Settings Persistence**: Remembers your server connection settings

### 🖥️ Server
- **FastAPI Backend**: High-performance async web framework
- **Railway Ready**: Pre-configured for Railway.com deployment
- **File Management**: Upload, download, list, and delete files
- **Thumbnail Generation**: Automatic image thumbnail creation
- **API Authentication**: Secure Bearer token authentication
- **Admin Interface**: Web-based file management dashboard

## 🚀 Quick Start

### Option 1: Use Pre-built Executable (Recommended)
1. Download `VRCPhoto2URL-Desktop.exe` from the `dist/` folder
2. Run the executable
3. Configure your server connection in settings
4. Start uploading files!

### Option 2: Run from Source
```bash
# Clone the repository
git clone https://github.com/yourusername/VRCPhoto2URL.git
cd VRCPhoto2URL

# Install client dependencies
cd client
pip install -r requirements.txt

# Launch the desktop client
python launch_desktop_client.py
```

### Server Setup (Railway Deployment)
1. Fork this repository
2. Connect your Railway account to GitHub
3. Deploy from the `server/` directory
4. Set environment variables:
   - `API_KEY`: Your chosen API key
   - `MAX_FILE_SIZE_MB`: Maximum file size (default: 50)

## 📁 Project Structure

```
VRCPhoto2URL/
├── client/                 # Desktop application
│   ├── src/               # Source code
│   ├── dist/              # Built executables
│   └── launch_desktop_client.py
├── server/                # FastAPI server
│   ├── src/               # Server source code
│   ├── static/            # Web interface files
│   ├── templates/         # HTML templates
│   └── requirements.txt
├── dist/                  # Distribution files
│   └── VRCPhoto2URL-Desktop.exe
└── docs-consolidated/     # Documentation
```

## 🔧 Development

### Building the Executable
```bash
cd client
python build_exe.py
```

### Running the Server Locally
```bash
cd server
pip install -r requirements.txt
python start.py
```

## 🌐 Server Endpoints

- `GET /health` - Server health check
- `POST /upload` - Upload files (requires API key)
- `GET /files` - List uploaded files
- `GET /files/{file_id}` - Download specific file
- `DELETE /files/{file_id}` - Delete specific file
- `GET /admin` - Admin web interface

## 🔐 Security

- **API Key Authentication**: All upload endpoints require valid API key
- **File Type Validation**: Configurable allowed file types
- **Size Limits**: Configurable maximum file size
- **UUID File Names**: Prevents path traversal and conflicts

## 📊 Recent Updates

### ✅ Issues Fixed (June 2025)
1. **URL Protocol Fix**: URLs now include proper `https://` or `http://` protocols
2. **Image Serving Enhancement**: Improved browser compatibility for image viewing
3. **Theme System**: Complete red-themed UI implementation
4. **Upload Functionality**: Fixed file list integration and copy URL feature

### 🎨 UI Improvements
- Modern dark theme with red accents
- Improved file upload workflow
- Enhanced activity tracking
- Better error handling and user feedback

## 🚀 Ready for Production

- ✅ **Desktop Client**: Fully functional with .exe distribution
- ✅ **Server**: Railway deployment ready
- ✅ **URL Generation**: Complete URLs with proper protocols
- ✅ **Cross-Platform**: Works on Windows, macOS, and Linux

## 📋 Requirements

### Desktop Client
- Python 3.8+
- PySide6
- Requests
- Windows/macOS/Linux

### Server
- Python 3.8+
- FastAPI
- Uvicorn
- PIL (Pillow)
- Railway account (for deployment)

## 🎯 Use Cases

- **VRChat Content Creators**: Quick screenshot sharing
- **Gaming Communities**: Easy image distribution
- **File Sharing**: Simple drag-and-drop file hosting
- **Screenshot Management**: Organized file storage with thumbnails

## 🔗 Links

- **Server Demo**: [Railway Deployment URL]
- **Documentation**: See `docs-consolidated/`
- **Build Scripts**: See `archive/build-scripts/`

## 📝 License

This project is open source. See the repository for license information.

---

**Made for VRChat communities and content creators** 🎮✨

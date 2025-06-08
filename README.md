# 🎮 VRCPhoto2URL - VRChat Screenshot Server

A professional file management server optimized for VRChat screenshots with modern desktop client.

## 🌟 **Features**

- **🚀 FastAPI Server** - High-performance REST API
- **🎮 VRChat Optimized** - Smart timing for large screenshot files
- **🖥️ Desktop Client** - Modern PySide6 interface with auto-upload
- **☁️ Railway Ready** - One-click cloud deployment
- **🔐 Secure** - API key authentication
- **📱 Admin Interface** - Web-based file management
- **🎯 VRCX Compatible** - Handles screenshot renaming

## 🚂 **Quick Railway Deployment**

1. **Fork this repository** to your GitHub
2. **Sign up** at [railway.app](https://railway.app)
3. **Deploy** the `custom-server-file-manager-1/server` folder
4. **Set API key** in Railway environment variables
5. **Done!** Your server is live

[📖 **Detailed Deployment Guide**](RAILWAY_DEPLOYMENT_GUIDE.md)

## 🎯 **Project Structure**

```
VRCPhoto2URL/
├── custom-server-file-manager-1/    # Main Project
│   ├── server/                       # 🚂 Railway Server (Deploy This)
│   │   ├── src/app.py               # FastAPI Application
│   │   ├── requirements.txt         # Dependencies
│   │   ├── Procfile                 # Railway Start Command
│   │   ├── static/                  # Web Assets
│   │   ├── templates/               # HTML Templates
│   │   └── uploads/                 # File Storage
│   ├── client/                      # 🖥️ Desktop Application
│   │   ├── src/                     # Client Source Code
│   │   ├── run_client.py           # Start Client
│   │   └── requirements.txt         # Client Dependencies
│   └── shared/                      # Shared Utilities
└── docs/                            # 📚 Documentation
```

## 🚀 **Quick Start**

### **1. Server (Railway)**
```bash
# Deploy to Railway (see deployment guide)
# Set API_KEY environment variable
# Server runs automatically
```

### **2. Desktop Client**
```bash
cd custom-server-file-manager-1/client
pip install -r requirements.txt
python run_client.py
```

## 🎮 **VRChat Integration**

This server is specifically optimized for VRChat screenshots:

- **Smart Delays** - 5 seconds for photos, 2 seconds for other files
- **Large File Support** - Enhanced retry logic for 5-10MB screenshots  
- **VRCX Compatible** - Handles file renaming from VRCX software
- **Auto-Upload** - Monitor VRChat photo folder for instant uploads

## 🔐 **Security**

- **API Key Authentication** - Secure access control
- **File Type Validation** - Only allowed file types
- **Size Limits** - Configurable file size limits (default 50MB)
- **HTTPS Ready** - Railway provides automatic SSL

## 📊 **Admin Features**

Access the admin interface at: `https://your-server.railway.app/admin`

- **File Management** - View, download, delete files
- **Statistics** - Upload counts, storage usage
- **Bulk Operations** - Delete old files automatically
- **Real-time Monitoring** - Live upload activity

## 🛠️ **API Endpoints**

```
POST /upload              # Upload file
GET  /files/{id}          # Download file
GET  /files/{id}/info     # File metadata
GET  /files               # List all files
DELETE /files/{id}        # Delete file
GET  /admin               # Admin interface
GET  /health              # Health check
```

## 📱 **Client Features**

- **Modern UI** - PySide6 desktop application
- **Auto-Upload** - Monitor folders for new files
- **VRChat Mode** - Optimized for screenshot workflow
- **Clipboard Integration** - Auto-copy URLs
- **Settings** - Customizable preferences

## 🔧 **Configuration**

### **Environment Variables**
```env
API_KEY=your-secret-key       # Required
PORT=8000                     # Railway sets this
MAX_FILE_SIZE=52428800        # 50MB limit
```

### **Client Settings**
```json
{
  "server_url": "https://your-app.railway.app",
  "api_key": "your-secret-key",
  "auto_upload": true,
  "vrchat_mode": true
}
```

## 🎯 **Perfect For**

- **VRChat Players** - Share screenshots instantly
- **Content Creators** - Quick file sharing
- **Communities** - Private file servers
- **Developers** - File API backend

## 📖 **Documentation**

- [Railway Deployment Guide](RAILWAY_DEPLOYMENT_GUIDE.md)
- [API Documentation](docs/api_documentation.md)
- [Client Setup](docs/client_setup.md)
- [Server Configuration](docs/server_setup.md)

## 🤝 **Support**

Need help? Check the documentation or open an issue!

---

**🚀 Ready to deploy your VRChat screenshot server? Start with Railway!**

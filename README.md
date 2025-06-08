# 🎮 VRCPhoto2URL - VRChat Screenshot Auto-Uploader

<div align="center">

![VRChat Logo](https://img.shields.io/badge/VRChat-Compatible-blue?style=for-the-badge&logo=vrchat)
![Railway](https://img.shields.io/badge/Railway-Deployed-success?style=for-the-badge&logo=railway)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=for-the-badge)

*Automatically upload your VRChat screenshots to the cloud and get instant shareable URLs*

[🚀 Quick Start](#-quick-start) • [📚 Documentation](#-documentation) • [🌐 Live Demo](#-live-demo) • [🛠️ Setup](#️-setup)

</div>

---

## ✨ Features

🎯 **Instant Upload** - Screenshots upload automatically when you take them in VRChat  
🔗 **Direct URLs** - Get shareable links copied to your clipboard instantly  
🖥️ **Desktop Client** - Beautiful GUI with auto-connection to cloud server  
🌐 **Cloud Hosting** - 24/7 server running on Railway.app  
📁 **VRChat Integration** - Monitors your VRChat Screenshots folder automatically  
🔄 **Auto-Sync** - No manual work needed - just take screenshots and share!  

## 🚀 Quick Start

### For VRChat Users (Easy Setup)

1. **Download & Launch**
   ```bash
   # Windows users: Double-click this file
   scripts/start_client.bat
   ```

2. **Auto-Connection**
   - Client connects to cloud server automatically
   - Green "Connected" status appears in 1 second

3. **Add VRChat Folder**
   - Click "📁 Add Folder" in the client
   - Navigate to: `%USERPROFILE%\Pictures\VRChat`
   - Select folder and enable monitoring

4. **Take Screenshots**
   - Press `F12` in VRChat (default screenshot key)
   - URLs are automatically copied to your clipboard
   - Share instantly by pasting anywhere!

### For Developers

```bash
# Clone repository
git clone https://github.com/your-username/VRCPhoto2URL.git
cd VRCPhoto2URL

# Install client dependencies
cd client
pip install -r requirements.txt

# Launch client
python src/modern_client.py

# Or use the launcher
python ../scripts/launch_client.py
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  VRChat Game    │    │  Desktop Client │    │  Railway Server │
│                 │    │                 │    │                 │
│  📸 Screenshot  │───▶│  📁 Monitor     │───▶│  ☁️ Upload      │
│  (F12 key)     │    │  🔄 Auto-upload │    │  🔗 Generate URL│
│                 │    │  📋 Copy URL    │    │  💾 Store File  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🌐 Live Demo

**Server**: https://vrcphoto2url-server-production.up.railway.app  
**Status**: ✅ Online and operational  
**Admin Panel**: Available at server URL  

## 📁 Project Structure

```
VRCPhoto2URL/
├── 📱 client/              # Desktop application
│   ├── src/                # Client source code
│   ├── client_config.json  # Auto-connection settings
│   └── requirements.txt    # Python dependencies
├── 🌐 server/              # Railway cloud server
│   ├── src/                # FastAPI server code
│   ├── start.py           # Railway startup script
│   └── requirements.txt    # Server dependencies
├── 🧪 tests/               # Test scripts and verification
├── 🔧 scripts/             # Setup and launch utilities
├── 📚 docs-consolidated/   # All documentation
└── 📋 README.md           # This file
```

## 🛠️ Setup Guide

### Prerequisites
- **Python 3.8+** installed
- **VRChat** game (for taking screenshots)
- **Windows** (primary support)

### Client Setup
1. Navigate to `client/` folder
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python src/modern_client.py`

### Server Setup (Optional - Already Deployed)
The server is already running on Railway.app, but if you want to deploy your own:

1. Fork this repository
2. Connect to Railway.app
3. Deploy the `server/` folder
4. Set environment variables (API key)

## 🎮 VRChat Integration

### Screenshot Folder Location
VRChat saves screenshots to:
```
C:\Users\[USERNAME]\Pictures\VRChat\
```

### Workflow
1. **Join VRChat world**
2. **Take screenshot** (F12)
3. **VRChat saves** image to folder
4. **Client detects** new file
5. **Auto-upload** to cloud server
6. **URL copied** to clipboard
7. **Share anywhere** by pasting!

### Supported Formats
- PNG (VRChat default)
- JPG/JPEG
- GIF, BMP, WebP

## 📊 Status & Monitoring

### System Status
- **Server**: ✅ Live on Railway.app
- **Client**: ✅ Desktop GUI working
- **Auto-connection**: ✅ Functional
- **VRChat Integration**: ✅ Ready
- **File Upload**: ✅ Operational

### Performance
- **Upload Speed**: Depends on file size and connection
- **Server Response**: ~100-300ms
- **Uptime**: 24/7 on Railway cloud
- **Storage**: Persistent cloud storage

## 🔧 Configuration

### Client Configuration (`client/client_config.json`)
```json
{
  "server_url": "https://vrcphoto2url-server-production.up.railway.app",
  "api_key": "your-secure-api-key",
  "auto_upload": true,
  "vrchat_mode": true,
  "remember_connection": true
}
```

### Environment Variables (Server)
```bash
PORT=8000              # Railway assigns this automatically
API_KEY=your-api-key   # Set in Railway dashboard
```

## 🛡️ Security

- **HTTPS**: All connections encrypted
- **API Authentication**: Secure token-based auth
- **File Validation**: Only image files accepted
- **Rate Limiting**: Prevents abuse

## 🔄 Updates & Deployment

### Client Updates
1. Download latest release
2. Replace client files
3. Keep `client_config.json` unchanged

### Server Updates
- Railway auto-deploys from GitHub
- Zero downtime deployments
- Persistent storage maintained

## 📚 Documentation

- **📖 [Complete Setup Guide](docs-consolidated/VRCHAT_SETUP_GUIDE.md)**
- **🚀 [Deployment Guide](docs-consolidated/RAILWAY_DEPLOYMENT_GUIDE.md)**
- **🧪 [Testing Documentation](docs-consolidated/FINAL_TESTING_REPORT.md)**
- **🔧 [API Documentation](docs-consolidated/api_documentation.md)**

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- **Issues**: [GitHub Issues](https://github.com/your-username/VRCPhoto2URL/issues)
- **Documentation**: Check `docs-consolidated/` folder
- **Server Status**: https://vrcphoto2url-server-production.up.railway.app/health

## 🎉 Credits

Built with ❤️ for the VRChat community

- **FastAPI** - Modern web framework
- **PySide6** - Desktop GUI framework
- **Railway.app** - Cloud hosting platform
- **VRChat** - The amazing social VR platform

---

<div align="center">

**Happy VRChatting! 📸🎮**

[![GitHub stars](https://img.shields.io/github/stars/your-username/VRCPhoto2URL?style=social)](https://github.com/your-username/VRCPhoto2URL)
[![Twitter Follow](https://img.shields.io/twitter/follow/your-twitter?style=social)](https://twitter.com/your-twitter)

</div>

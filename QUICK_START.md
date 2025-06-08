# 🚀 VRCPhoto2URL Quick Start Guide

*Get up and running in 2 minutes!*

## 🎯 What This Does

Upload your VRChat screenshots to the cloud automatically and get instant shareable URLs copied to your clipboard.

## ⚡ Super Quick Setup

### Option A: Interactive Setup (Recommended)
```bash
# Windows: Double-click this file
scripts\start_client.bat

# The launcher will guide you through:
# 1. Enter your Railway server URL
# 2. Generate or enter API key  
# 3. Test connection
# 4. Launch client
```

### Option B: Quick Demo Setup
```bash
# For immediate testing with demo server
python setup_demo.py

# Then launch client
scripts\start_client.bat
```

### Option C: Manual Configuration
```bash
# Copy template and edit manually
copy client\client_config.json.example client\client_config.json

# Edit client\client_config.json with your settings:
# - server_url: Your Railway app URL
# - api_key: Your API key from Railway environment
```

### Step 2: Auto-Connection ✅
Once configured, the client automatically connects to your server. You'll see:
- Green "✅ Connected" status  
- Server URL displayed
- Ready to upload!

### Step 3: Add VRChat Folder 📁
1. Click **"📁 Add Folder"** in the client
2. Navigate to: `C:\Users\[YourName]\Pictures\VRChat`
3. Select the folder
4. ✅ "Auto Upload" should already be enabled

### Step 4: Take Screenshots 📸
1. Open VRChat
2. Press `F12` to take a screenshot
3. 🎉 URL is automatically copied to your clipboard!
4. Paste anywhere to share your screenshot

## 🔧 Troubleshooting

### Client Won't Start?
```bash
# Install dependencies
cd client
pip install -r requirements.txt
```

### Can't Find VRChat Folder?
In VRChat, go to: **Settings → Camera → Photo Path**

### Connection Issues?
Check if this URL works: https://vrcphoto2url-server-production.up.railway.app/health

## 🎮 Pro Tips

- **Custom Screenshot Key**: Change in VRChat settings
- **File Types**: PNG (default), JPG, GIF all supported
- **Sharing**: URLs work on Discord, Twitter, Reddit, etc.
- **No Limits**: Upload as many screenshots as you want!

## 📞 Need Help?

- 📚 **Full Documentation**: See `docs-consolidated/` folder
- 🧪 **Test Connection**: Run `python tests/verify_deployment.py`
- 🌐 **Server Status**: https://vrcphoto2url-server-production.up.railway.app

---

**That's it! Now go take some amazing VRChat screenshots! 📸✨**

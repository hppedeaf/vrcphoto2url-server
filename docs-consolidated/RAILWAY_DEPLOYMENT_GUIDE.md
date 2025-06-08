# 🚂 Railway.com Deployment Guide for VRCPhoto2URL Server

## 📋 **Prerequisites**

1. **GitHub Account** - Your code needs to be in a GitHub repository
2. **Railway Account** - Sign up at [railway.app](https://railway.app)
3. **Clean Project Structure** - ✅ Already completed!

---

## 🎯 **Step-by-Step Railway Deployment**

### **1. Prepare Your Repository**

First, ensure your project is in a GitHub repository:

```bash
# If not already a git repo
git init
git add .
git commit -m "Initial commit - VRCPhoto2URL Server"

# Create repository on GitHub and push
git remote add origin https://github.com/yourusername/vrcphoto2url.git
git branch -M main
git push -u origin main
```

### **2. Railway Project Setup**

1. **Go to Railway**: Visit [railway.app](https://railway.app)
2. **Sign Up/Login**: Use GitHub authentication
3. **New Project**: Click "New Project"
4. **Deploy from GitHub**: Select "Deploy from GitHub repo"
5. **Select Repository**: Choose your VRCPhoto2URL repository
6. **Select Service**: Choose the `custom-server-file-manager-1/server` folder

### **3. Railway Configuration**

Railway will automatically detect your Python project and use these files:

#### **✅ Already Configured Files:**
- `requirements.txt` - Python dependencies
- `Procfile` - Railway start command
- `railway.json` - Build and deploy configuration

#### **🔧 Environment Variables to Set:**

In Railway Dashboard → Your Project → Variables:

```
API_KEY=your-super-secret-api-key-change-this
PORT=8000
HOST=0.0.0.0
RAILWAY_STATIC_URL=https://your-app.railway.app
```

### **4. Deploy Your Server**

1. **Connect Repository**: Railway will automatically deploy when you push
2. **Monitor Deployment**: Watch the build logs in Railway dashboard
3. **Get Your URL**: Railway provides a URL like `https://your-app.railway.app`

---

## 🔧 **Project Structure for Railway**

Your clean project structure is now:

```
VRCPhoto2URL/
├── custom-server-file-manager-1/
│   ├── server/                     # 🚂 Railway deploys this folder
│   │   ├── src/
│   │   │   └── app.py             # Main FastAPI application
│   │   ├── requirements.txt        # Python dependencies
│   │   ├── Procfile               # Railway start command
│   │   ├── railway.json           # Railway configuration
│   │   ├── static/                # Static files (CSS, JS)
│   │   ├── templates/             # HTML templates
│   │   └── uploads/               # File storage (persistent)
│   ├── client/                    # Desktop client (not deployed)
│   └── shared/                    # Shared utilities
├── docs/                          # 📚 All documentation moved here
└── README.md                      # Main project README
```

---

## 🌟 **Railway Deployment Features**

### **✅ What Railway Provides:**
- **Automatic Deployments** - Deploys on git push
- **HTTPS SSL** - Automatic SSL certificates
- **Environment Variables** - Secure config management
- **Persistent Storage** - Files survive deployments
- **Custom Domains** - Connect your own domain
- **Monitoring** - Built-in metrics and logs

### **💰 Pricing:**
- **Hobby Plan**: $5/month - Perfect for personal projects
- **Generous Free Tier**: $5 credit monthly (enough for small usage)

---

## 🚀 **Deployment Commands**

### **One-Time Setup:**
```bash
# 1. Install Railway CLI (optional)
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Link to your project
railway link
```

### **Deploy Updates:**
```bash
# Just push to GitHub - Railway auto-deploys!
git add .
git commit -m "Update server"
git push
```

---

## 🔐 **Security Configuration**

### **Important Environment Variables:**

```env
# Required - Change this!
API_KEY=your-super-secret-api-key-12345

# Railway sets these automatically
PORT=8000
RAILWAY_STATIC_URL=https://your-app.railway.app

# Optional - for advanced configs
MAX_FILE_SIZE=52428800  # 50MB in bytes
UPLOAD_RETENTION_DAYS=30
```

### **API Key Generation:**
```bash
# Generate a secure API key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 📊 **After Deployment**

### **Test Your Deployment:**

1. **Health Check**: `https://your-app.railway.app/health`
2. **API Root**: `https://your-app.railway.app/`
3. **Admin Interface**: `https://your-app.railway.app/admin`

### **Configure Your Client:**
Update your desktop client to use:
```
Server URL: https://your-app.railway.app
API Key: your-super-secret-api-key-12345
```

---

## 🛠️ **Troubleshooting**

### **Common Issues:**

1. **Build Fails**: Check `requirements.txt` is in `/server/` folder
2. **App Won't Start**: Verify `Procfile` and `railway.json`
3. **File Uploads Fail**: Check API key configuration
4. **Static Files 404**: Ensure `static/` and `templates/` folders exist

### **View Logs:**
```bash
railway logs
```

---

## 🎉 **You're Ready!**

Your VRCPhoto2URL server will be live at:
**`https://your-app.railway.app`**

The admin interface will be at:
**`https://your-app.railway.app/admin`**

Your VRChat screenshots can now be uploaded to a professional cloud server! 🎮📸

---

*Need help? Check Railway's documentation at [docs.railway.app](https://docs.railway.app)*

# 🚀 **COMPLETE RAILWAY DEPLOYMENT INSTRUCTIONS**

## 🎯 **What You'll Deploy**

Your VRCPhoto2URL server will be a professional cloud service at a URL like:
**`https://vrcphoto2url-production.railway.app`**

---

## 📋 **Before You Start**

✅ **GitHub Account** - Free at [github.com](https://github.com)  
✅ **Railway Account** - Free at [railway.app](https://railway.app)  
✅ **Clean Project** - ✅ Already done!

---

## 🚀 **STEP 1: Prepare GitHub Repository**

### **Option A: Create New Repository**
1. Go to [github.com](https://github.com) → **New Repository**
2. Name: `vrcphoto2url-server`
3. Description: `VRChat Screenshot Upload Server`
4. **Public** (or Private if you prefer)
5. Click **Create Repository**

### **Option B: Use Existing Repository**
If you already have this code on GitHub, skip to Step 2.

### **Upload Your Code:**
```powershell
# Navigate to your project
cd "d:\developpeur\VRCPhoto2URL"

# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - VRCPhoto2URL Server ready for Railway"

# Connect to GitHub (replace with your repo URL)
git remote add origin https://github.com/YOURUSERNAME/vrcphoto2url-server.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## 🚂 **STEP 2: Deploy to Railway**

### **A. Sign Up & Connect GitHub**
1. Go to [railway.app](https://railway.app)
2. Click **Login with GitHub**
3. Authorize Railway to access your repositories

### **B. Create New Project**
1. Click **New Project**
2. Select **Deploy from GitHub repo**
3. Choose your `vrcphoto2url-server` repository
4. Railway will scan and detect your Python project

### **C. Configure Deployment**
1. **Root Directory**: Set to `custom-server-file-manager-1/server`
2. **Build Command**: `pip install -r requirements.txt` (auto-detected)
3. **Start Command**: `cd src && uvicorn app:app --host 0.0.0.0 --port $PORT` (from Procfile)

---

## 🔐 **STEP 3: Set Environment Variables**

In Railway Dashboard → Your Project → **Variables** tab:

### **Required Variables:**
```
API_KEY = your-super-secret-api-key-change-this-now
```

### **Optional Variables:**
```
MAX_FILE_SIZE = 52428800
UPLOAD_RETENTION_DAYS = 30
```

⚠️ **IMPORTANT**: Change `API_KEY` to something secure!

**Generate Secure API Key:**
```powershell
python -c "import secrets; print('API_KEY=' + secrets.token_urlsafe(32))"
```

---

## 🌐 **STEP 4: Get Your Live URL**

1. Railway will build and deploy automatically
2. Click **Deployments** → View build logs
3. Once deployed, click **Settings** → **Domains**
4. You'll see a URL like: `https://vrcphoto2url-production-a1b2c3.railway.app`

---

## ✅ **STEP 5: Test Your Deployment**

### **Test Endpoints:**
```
🏠 Homepage: https://your-app.railway.app/
💚 Health: https://your-app.railway.app/health
👑 Admin: https://your-app.railway.app/admin
```

### **Expected Responses:**
- **Homepage**: `{"message":"Custom Server File Manager API","version":"1.0.0","status":"running"}`
- **Health**: `{"status":"healthy","timestamp":"2025-06-08T..."}`
- **Admin**: HTML admin interface

---

## 🖥️ **STEP 6: Configure Desktop Client**

Update your desktop client settings:

```json
{
  "server_url": "https://your-app.railway.app",
  "api_key": "your-super-secret-api-key-change-this-now"
}
```

---

## 💰 **RAILWAY PRICING**

### **Free Tier:**
- ✅ $5 monthly credit
- ✅ Perfect for personal use
- ✅ Automatic HTTPS
- ✅ Custom domains

### **Pro Plan ($5/month):**
- ✅ $5 credit + $5 included usage
- ✅ Higher limits
- ✅ Priority support

**For VRChat screenshots**: Free tier is usually sufficient!

---

## 🔧 **ADVANCED CONFIGURATION**

### **Custom Domain (Optional):**
1. Railway → Settings → **Domains**
2. Add your domain: `vrchat.yourdomain.com`
3. Configure DNS as instructed
4. Automatic SSL certificate

### **Environment Files:**
Railway reads these files automatically:
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Start command
- ✅ `railway.json` - Build configuration
- ✅ `Dockerfile` - Container setup (optional)

---

## 🚨 **TROUBLESHOOTING**

### **Build Fails:**
- ✅ Check `requirements.txt` exists in `/server/` folder
- ✅ Verify root directory is set to `custom-server-file-manager-1/server`

### **App Won't Start:**
- ✅ Check environment variables are set
- ✅ View logs in Railway Dashboard → **Deployments**

### **Upload Fails:**
- ✅ Verify API key matches between server and client
- ✅ Check file size limits

### **View Logs:**
Railway Dashboard → **Deployments** → Click latest deployment → **View Logs**

---

## 🎉 **DEPLOYMENT COMPLETE!**

Your VRChat screenshot server is now live at:
**`https://your-app.railway.app`**

### **What You Can Do:**
- 📸 **Upload VRChat Screenshots** via desktop client
- 🌐 **Share Files** with direct URLs
- 👑 **Manage Files** via admin interface
- 📊 **Monitor Usage** with built-in stats
- 🔐 **Secure Access** with API key authentication

### **Next Steps:**
1. **Configure Client** with your server URL
2. **Test Uploads** with some VRChat screenshots
3. **Share URLs** with friends
4. **Monitor Usage** in admin panel

---

## 🆘 **NEED HELP?**

- 📖 **Railway Docs**: [docs.railway.app](https://docs.railway.app)
- 💬 **Railway Discord**: [discord.gg/railway](https://discord.gg/railway)
- 🐛 **Issues**: Create issue in your GitHub repo

---

**🚀 Your VRChat screenshot server is now PRODUCTION READY!**

*Deployment completed on June 8, 2025* ✨

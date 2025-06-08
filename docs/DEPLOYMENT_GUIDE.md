# Custom File Server - Complete Setup Guide

This guide will help you deploy the server and run the client for the Custom File Server application.

## Overview

This project consists of two parts:
- **Server**: A FastAPI-based backend that handles file storage and management
- **Client**: A PySide6 desktop application that connects to the server

## Part 1: Server Deployment (Railway.com)

### Prerequisites
- Railway.com account (free tier available)
- GitHub account
- Your project code pushed to GitHub

### Step 1: Prepare for Deployment

1. **Ensure your server code is ready**:
   ```
   custom-server-file-manager-1/
   └── server/
       ├── src/app.py
       ├── requirements.txt
       ├── Procfile
       ├── railway.json
       └── .env.example
   ```

2. **Push your code to GitHub** (if not already done)

### Step 2: Deploy to Railway

1. **Visit [railway.app](https://railway.app)** and sign in with GitHub

2. **Create a new project**:
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Select the `server` folder as the root directory

3. **Configure environment variables**:
   - Go to your project dashboard
   - Click "Variables" tab
   - Add these variables:
     ```
     API_KEY=your-chosen-secure-api-key-here
     ENVIRONMENT=production
     MAX_FILE_SIZE_MB=50
     ```

4. **Deploy**:
   - Railway will automatically build and deploy your server
   - Wait for deployment to complete (usually 2-3 minutes)
   - Note your server URL (e.g., `https://your-app.railway.app`)

### Step 3: Test Your Deployment

1. **Test health endpoint**:
   ```bash
   curl https://your-app.railway.app/health
   ```
   Should return: `{"status":"healthy","timestamp":"..."}`

2. **Test API documentation**:
   Visit: `https://your-app.railway.app/docs`

## Part 2: Client Setup and Usage

### Step 1: Install Client Dependencies

1. **Navigate to client directory**:
   ```powershell
   cd custom-server-file-manager-1\client
   ```

2. **Install Python dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

### Step 2: Run the Client

1. **Start the client application**:
   ```powershell
   python run_client.py
   ```

2. **The GUI application will open**

### Step 3: Connect to Your Server

1. **Click "Connect to Server"** in the client

2. **Enter connection details**:
   - **Server URL**: `https://your-app.railway.app`
   - **API Key**: The same key you set in Railway environment variables

3. **Test connection** by clicking "Test Connection"

4. **Connect** once the test succeeds

### Step 4: Use the Application

Once connected, you can:
- **Upload files**: Click "Upload File" and select files
- **View files**: All uploaded files appear in the right panel
- **Download files**: Double-click any file or select and click "Download Selected"
- **Copy URLs**: Select a file and click "Copy URL" for direct sharing
- **Delete files**: Select a file and click "Delete Selected"

## Troubleshooting

### Server Issues

**Deployment failed**:
1. Check Railway deployment logs
2. Verify all files are in the `server` directory
3. Ensure `requirements.txt` is correct
4. Check that `Procfile` exists and is correctly configured

**Server not responding**:
1. Check Railway service status
2. Verify environment variables are set
3. Check logs for error messages

### Client Issues

**Connection failed**:
1. Verify server URL is correct and includes `https://`
2. Check that API key matches the one set in Railway
3. Ensure your internet connection is working
4. Test the health endpoint in a web browser

**Installation errors**:
```powershell
# Try upgrading pip first
python -m pip install --upgrade pip
pip install --upgrade -r requirements.txt
```

**GUI not appearing**:
1. Ensure you're using Python 3.8+
2. Try running from different directory
3. Check that PySide6 installed correctly:
   ```powershell
   python -c "from PySide6.QtWidgets import QApplication; print('PySide6 working')"
   ```

## Security Notes

- **Keep your API key secure** - don't share it publicly
- **Use HTTPS** - Railway provides HTTPS by default
- **Regular backups** - Railway doesn't guarantee data persistence on free tier
- **Monitor usage** - Be aware of Railway's usage limits

## Advanced Configuration

### Custom Domain (Railway Pro)
1. Go to Railway dashboard
2. Click "Settings" → "Domains"
3. Add your custom domain
4. Update DNS records as instructed

### Scaling (Railway Pro)
1. Adjust resource allocation in Railway dashboard
2. Monitor performance metrics
3. Consider upgrading plan for production use

### Environment-Specific Settings

**Development**:
```env
API_KEY=dev-key-123
ENVIRONMENT=development
MAX_FILE_SIZE_MB=10
```

**Production**:
```env
API_KEY=secure-production-key-here
ENVIRONMENT=production
MAX_FILE_SIZE_MB=50
```

## Support

If you encounter issues:

1. **Check the logs**: Railway provides detailed deployment and runtime logs
2. **Verify configuration**: Ensure all environment variables are set correctly
3. **Test locally**: Try running the server locally first to isolate issues
4. **Check documentation**: Review the README files in both server and client directories

## Next Steps

- **Backup strategy**: Implement regular file backups
- **User management**: Add user authentication if needed
- **Monitoring**: Set up monitoring and alerts
- **Custom features**: Extend the API and client for your specific needs

The application is now ready for personal use with secure file storage and management!

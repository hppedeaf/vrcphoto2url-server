# 🚂 Railway Deployment Files
# These files configure automatic deployment

## Required Files:
- requirements.txt  # Python dependencies
- Procfile         # Start command  
- railway.json     # Build configuration
- .env.example     # Environment template

## Environment Variables (Set in Railway):
API_KEY=your-super-secret-key
PORT=8000
RAILWAY_STATIC_URL=https://your-app.railway.app

## Deployment:
1. Push to GitHub
2. Connect to Railway
3. Deploy server/ folder
4. Set environment variables
5. Your server is live!

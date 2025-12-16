# Cricket Analytics Deployment Guide

## Quick Public Link (ngrok) - FASTEST

### Step 1: Download ngrok
1. Go to: https://ngrok.com/download
2. Download for Windows
3. Extract `ngrok.exe` to this project folder

### Step 2: Start Application
Open 2 terminals:

**Terminal 1 - Start Flask:**
```bash
cd "d:/Cricket Project"
python webapp/app.py
```

**Terminal 2 - Create Public URL:**
```bash
cd "d:/Cricket Project"
ngrok http 5000
```

### Step 3: Share the URL
ngrok will display a URL like: `https://abc123.ngrok-free.app`
Share this URL with anyone!

---

## Production Deployment (Render.com) - PERMANENT

### Prerequisites
- GitHub account
- Render.com account (free)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "IPL Analytics Dashboard"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to https://render.com/
2. Sign in with GitHub
3. Click "New +" → "Web Service"
4. Connect your repository
5. Settings:
   - **Name:** ipl-analytics
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn --chdir webapp app:app`
6. Click "Create Web Service"

### Step 3: Get Your URL
Render will provide a permanent URL like:
`https://ipl-analytics.onrender.com`

**Note:** First load may take 30-60 seconds (free tier)

---

## Alternative: Railway.app

1. Go to https://railway.app/
2. "Start a New Project" → "Deploy from GitHub"
3. Select your repository
4. Railway auto-detects Flask and deploys
5. Get your URL from the Deployments tab

---

## Recommended: Use ngrok for immediate testing

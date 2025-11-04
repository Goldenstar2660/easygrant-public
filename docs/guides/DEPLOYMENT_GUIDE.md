# 🚀 EasyGrant Deployment Guide - FREE Hosting

Deploy your EasyGrant application to the web for **completely free** using Render (backend) + Vercel (frontend).

## 📋 Prerequisites

- GitHub account (to push your code)
- Render account (free): https://render.com
- Vercel account (free): https://vercel.com
- Your OpenAI API key

---

## 🎯 Quick Deployment (3 Steps)

### Step 1: Push Code to GitHub ✅

```powershell
# Initialize git (if not already done)
cd "C:\Users\Derek Chen\Desktop\Derek\Projects\EasyGrant"
git init
git add .
git commit -m "Initial commit - Ready for deployment"

# Create a new repository on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/EasyGrant.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy Backend to Render 🔧

1. **Go to** https://render.com and sign in
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Render will **auto-detect** your `render.yaml` configuration
5. Click **"Apply"** to use the blueprint
6. **Set environment variable**:
   - Go to **Environment** tab
   - Add: `OPENAI_API_KEY` = `your-openai-api-key-here`
7. Click **"Create Web Service"**
8. Wait 5-10 minutes for deployment
9. **Copy your backend URL**: `https://easygrant-XXXX.onrender.com`

### Step 3: Deploy Frontend to Vercel 🎨

1. **Go to** https://vercel.com and sign in
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. **Add Environment Variable**:
   - Key: `VITE_API_URL`
   - Value: `https://easygrant-XXXX.onrender.com` (your Render URL)
6. Click **"Deploy"**
7. Wait 2-3 minutes
8. **Your site is live!** 🎉

---

## 🔧 Update Backend CORS Settings

After deployment, update your backend to allow requests from your Vercel frontend:

```powershell
# Edit backend/src/main.py
```

Find the CORS_ORIGINS section and add your Vercel URL:

```python
CORS_ORIGINS = [
    "http://localhost:5173",  # Local development
    "http://localhost:3000",
    "https://easygrant-YOUR-PROJECT.vercel.app",  # Add your Vercel URL
]
```

Then commit and push:

```powershell
git add backend/src/main.py
git commit -m "Update CORS for production"
git push
```

Render will auto-deploy the update!

---

## 💰 Free Tier Limits

### Render Free Tier:
- ✅ **RAM**: 512 MB
- ✅ **Storage**: 1 GB disk
- ✅ **Bandwidth**: 100 GB/month
- ⚠️ **Sleeps after 15 min inactivity** (wakes up on request, ~30s delay)
- ⚠️ **750 free hours/month** (≈31 days if running 24/7)
- ⚠️ **NOT true 24/7 uptime** on free tier

**Important**: If your backend is constantly active 24/7, you'll hit the 750-hour monthly limit and service will stop until next billing cycle. For production, consider upgrading to Render Starter ($7/month) for always-on service.

See **[Render Free Tier Solutions](RENDER_FREE_TIER_SOLUTIONS.md)** for detailed strategies.

### Vercel Free Tier:
- ✅ **Bandwidth**: 100 GB/month
- ✅ **Builds**: Unlimited
- ✅ **Always on** (no sleep)
- ✅ Free SSL certificate

---

## 🌐 Your Live URLs

After deployment, you'll have:

- **Frontend**: `https://easygrant-YOUR-PROJECT.vercel.app`
- **Backend API**: `https://easygrant-XXXX.onrender.com`
- **API Docs**: `https://easygrant-XXXX.onrender.com/docs`

---

## 🔄 Alternative: Deploy Both to Render

If you prefer a single platform, you can deploy both backend and frontend to Render:

### Update `render.yaml`:

```yaml
services:
  # Backend
  - type: web
    name: easygrant-api
    runtime: docker
    plan: free
    envVars:
      - key: OPENAI_API_KEY
        sync: false
    healthCheckPath: /health
    dockerfilePath: ./Dockerfile
    autoDeploy: true

  # Frontend (Static Site)
  - type: web
    name: easygrant-frontend
    runtime: node
    plan: free
    buildCommand: cd frontend && npm install && npm run build
    staticPublishPath: ./frontend/dist
    envVars:
      - key: VITE_API_URL
        value: https://easygrant-api.onrender.com
    routes:
      - type: rewrite
        source: /*
        destination: /index.html
```

---

## 🐛 Troubleshooting

### Backend won't start on Render:
1. Check **Logs** tab in Render dashboard
2. Verify `OPENAI_API_KEY` is set in Environment variables
3. Check if build completed successfully

### Frontend can't connect to backend:
1. Verify `VITE_API_URL` environment variable in Vercel
2. Check CORS settings in `backend/src/main.py`
3. Make sure backend URL is correct (no trailing slash)

### Render service keeps sleeping:
- Free tier sleeps after 15 minutes of inactivity
- First request after sleep takes ~30 seconds
- Upgrade to paid tier ($7/month) for always-on service

---

## 📊 Monitoring Your App

### Render Dashboard:
- View logs in real-time
- Monitor CPU/RAM usage
- See deployment history
- Check health status

### Vercel Dashboard:
- View deployment logs
- Monitor bandwidth usage
- See build analytics
- Check performance metrics

---

## 🔒 Security Checklist

Before going live:

- [ ] Remove any hardcoded API keys from code
- [ ] Set `OPENAI_API_KEY` in Render environment variables (not in code)
- [ ] Update CORS origins to include production URLs
- [ ] Review `.gitignore` to ensure `.env` is not committed
- [ ] Enable Render's free SSL (automatic)
- [ ] Set up Vercel's free SSL (automatic)

---

## 🚀 CI/CD (Continuous Deployment)

Both Render and Vercel support automatic deployments:

1. **Push to GitHub** → Automatically triggers deployment
2. **Monitor in dashboards** → See build progress
3. **Auto-rollback** if deployment fails
4. **Preview deployments** for pull requests (Vercel)

---

## 💡 Pro Tips

1. **Keep main branch stable** - Use feature branches for development
2. **Test locally first** - Use `start-backend.ps1` and `start-frontend.ps1`
3. **Monitor free tier usage** - Check Render/Vercel dashboards monthly
4. **Use environment variables** - Never commit secrets to git
5. **Check logs regularly** - Catch errors early

---

## 🎓 Next Steps

After deployment:

1. Share your live URL: `https://easygrant-YOUR-PROJECT.vercel.app`
2. Test all features in production
3. Monitor error logs
4. Set up custom domain (optional, ~$10/year)
5. Consider upgrading if you exceed free tier limits

---

## 📞 Need Help?

- **Render Docs**: https://render.com/docs
- **Vercel Docs**: https://vercel.com/docs
- **OpenAI Status**: https://status.openai.com

Your app is ready to deploy! 🎉

Choose your deployment method and follow the steps above. Both are completely free and production-ready.

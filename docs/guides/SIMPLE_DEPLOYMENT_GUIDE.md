# 🚀 Simple Deployment Guide - Start to Finish

**Goal**: Deploy EasyGrant to production in ~20 minutes.

**What you'll get**:
- Frontend on Vercel (fast, global CDN)
- Backend on Render (persistent storage)
- Total cost: $0/month (with limitations) or $7/month (production-ready)

---

## Prerequisites (5 minutes)

### 1. Create Accounts

**GitHub** (if you don't have one):
- Go to https://github.com
- Sign up for free account

**Render**:
- Go to https://render.com
- Click "Get Started"
- Sign up with GitHub (easiest)

**Vercel**:
- Go to https://vercel.com
- Click "Sign Up"
- Sign up with GitHub (easiest)

### 2. Get Your OpenAI API Key

- Go to https://platform.openai.com/api-keys
- Click "Create new secret key"
- Copy the key (starts with `sk-`)
- **Save it somewhere safe** - you'll need it soon!

---

## Step 1: Push Code to GitHub (5 minutes)

Open PowerShell in your project folder:

```powershell
# Navigate to your project
cd C:\Users\hello\Documents\Projects\EasyGrant

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Ready for deployment"

# Create repository on GitHub
# Go to https://github.com/new
# Repository name: EasyGrant
# Keep it public (or private, your choice)
# Click "Create repository"

# Link your local repo to GitHub (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/EasyGrant.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**✅ Checkpoint**: Your code is now on GitHub!

---

## Step 2: Deploy Backend to Render (8 minutes)

### A. Create Web Service

1. Go to https://dashboard.render.com
2. Click **"New +"** button (top right)
3. Click **"Web Service"**

### B. Connect Repository

1. Click **"Build and deploy from a Git repository"**
2. Click **"Connect"** next to your GitHub account
3. Find and select your **"EasyGrant"** repository
4. Click **"Connect"**

### C. Configure Service

Render will auto-detect your `render.yaml`. Click **"Apply"** to use it.

**OR** if it doesn't auto-detect, manually configure:

```
Name: easygrant
Region: Oregon (or closest to you)
Branch: main
Runtime: Docker
Dockerfile Path: ./Dockerfile
Plan: Free
```

### D. Set Environment Variable

1. Scroll down to **"Environment Variables"**
2. Click **"Add Environment Variable"**
3. Add:
   - **Key**: `OPENAI_API_KEY`
   - **Value**: `sk-...` (paste your OpenAI API key)
4. Click **"Add"**

### E. Deploy

1. Click **"Create Web Service"**
2. Wait 5-10 minutes for deployment
3. You'll see build logs scrolling

**✅ Checkpoint**: When you see "Your service is live", continue!

### F. Copy Your Backend URL

At the top of the page, you'll see:
```
https://easygrant-XXXX.onrender.com
```

**Copy this URL** - you'll need it for Vercel!

---

## Step 3: Deploy Frontend to Vercel (5 minutes)

### A. Import Project

1. Go to https://vercel.com/dashboard
2. Click **"Add New..."** button
3. Click **"Project"**
4. Click **"Import"** next to your **EasyGrant** repository

### B. Configure Build Settings

**Framework Preset**: Select **"Vite"**

**Root Directory**: Type **`frontend`**

**Build Command**: `npm run build` (should auto-fill)

**Output Directory**: `dist` (should auto-fill)

**Install Command**: `npm install` (should auto-fill)

### C. Add Environment Variable

1. Click **"Environment Variables"** section
2. Add variable:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://easygrant-XXXX.onrender.com` (your Render URL from Step 2F)
   - **Environments**: Check all boxes (Production, Preview, Development)

**⚠️ IMPORTANT**: 
- No trailing slash: ✅ `.../onrender.com` ❌ `.../onrender.com/`
- Must start with `https://`

### D. Deploy

1. Click **"Deploy"**
2. Wait 2-3 minutes
3. You'll see build progress

**✅ Checkpoint**: When build completes, you'll see "Congratulations!"

### E. Copy Your Frontend URL

You'll see:
```
https://easygrant-USERNAME.vercel.app
```

**Copy this URL** - you need it for the next step!

---

## Step 4: Update Backend CORS (2 minutes)

Your frontend needs permission to talk to your backend.

### A. Edit Code Locally

Open `backend/src/main.py` in VS Code.

Find this section (around line 51):

```python
CORS_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",   # Alternative dev port
]
```

**Change it to** (replace with YOUR Vercel URL):

```python
CORS_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",   # Alternative dev port
    "https://easygrant-USERNAME.vercel.app",  # Your Vercel URL
    "https://easygrant-*-USERNAME.vercel.app",  # Vercel preview deployments
]
```

### B. Commit and Push

```powershell
# Save the file in VS Code

# In PowerShell:
git add backend/src/main.py
git commit -m "Add Vercel CORS origins"
git push
```

### C. Wait for Render to Redeploy

1. Go to Render dashboard
2. You'll see "Deploying..." in your service
3. Wait ~2-3 minutes for it to finish

**✅ Checkpoint**: When it says "Live", continue!

---

## Step 5: Test Your Deployment (2 minutes)

### A. Test Backend

Open in browser:
```
https://easygrant-XXXX.onrender.com/health
```

**Should show**:
```json
{"status":"healthy"}
```

### B. Test API Documentation

Open in browser:
```
https://easygrant-XXXX.onrender.com/docs
```

**Should show**: Swagger UI with all API endpoints

### C. Test Frontend

Open in browser:
```
https://easygrant-USERNAME.vercel.app
```

**Should show**: Your EasyGrant interface

### D. Test Full Flow

1. Click anywhere in the app
2. **⚠️ If this is the first request in 15+ minutes**, it will take ~30 seconds (backend waking up)
3. After that, everything should be fast!

**Try**:
- Creating a new session (should work)
- Check browser console (F12) - should be no errors
- If you see CORS errors, double-check Step 4

---

## 🎉 Success!

**Your URLs**:
- Frontend: `https://easygrant-USERNAME.vercel.app`
- Backend: `https://easygrant-XXXX.onrender.com`
- API Docs: `https://easygrant-XXXX.onrender.com/docs`

**From now on**:
- Every `git push` = automatic deployment to both platforms!
- Changes take 2-5 minutes to go live

---

## ⚠️ Important: Free Tier Limitations

**Render Free Tier**:
- ⚠️ Sleeps after 15 minutes of inactivity
- ⚠️ First request after sleep = 30 seconds wait
- ⚠️ 750 hours/month limit (~31 days if running 24/7)
- ⚠️ Service stops if you exceed 750 hours

**For Production Use**:
- Consider upgrading to Render Starter: **$7/month**
- Removes sleep, no hour limits, better performance
- Dashboard → Your service → "Upgrade" button

See `RENDER_FREE_TIER_SOLUTIONS.md` for details.

---

## 🐛 Troubleshooting

### Problem: Blank page on Vercel

**Check**:
1. Open browser console (F12)
2. Look for errors

**Common fixes**:
- Vercel → Settings → Environment Variables
- Verify `VITE_API_URL` is correct
- Click "Redeploy"

### Problem: CORS errors

**Error looks like**:
```
Access to fetch blocked by CORS policy
```

**Fix**:
1. Verify you did Step 4 correctly
2. Check `backend/src/main.py` has your Vercel URL
3. Verify you pushed the changes
4. Wait for Render to finish deploying

### Problem: Backend returns 503

**Cause**: Backend is sleeping (free tier)

**Fix**:
- Wait 30 seconds and try again
- It's waking up
- This is normal on free tier

### Problem: "Free tier hours exceeded"

**Cause**: You used all 750 hours this month

**Fix**:
- Wait until next month (1st of next month)
- OR upgrade to paid tier ($7/month)

---

## 📊 Next Steps

### Monitor Your Deployment

**Render Dashboard**:
- https://dashboard.render.com
- Check logs, metrics, uptime

**Vercel Dashboard**:
- https://vercel.com/dashboard
- Check deployments, analytics

### Set Up Monitoring (Optional)

**UptimeRobot** (free):
1. Sign up: https://uptimerobot.com
2. Add monitor for your backend
3. Get email alerts if it goes down

### Custom Domain (Optional)

**Vercel**:
1. Dashboard → Your project → Settings → Domains
2. Add your domain (e.g., `easygrant.com`)
3. Follow DNS instructions
4. Free SSL certificate included!

---

## 💡 Pro Tips

### Faster Deployments

**Preview Deployments**:
- Push to any branch = preview URL
- Test before merging to main
- Great for testing features

**Example**:
```powershell
# Create feature branch
git checkout -b new-feature

# Make changes
# ...

# Push
git push origin new-feature

# Vercel creates preview: https://easygrant-git-new-feature-USERNAME.vercel.app
```

### View Logs

**Render**:
- Dashboard → Your service → "Logs" tab
- See real-time backend logs

**Vercel**:
- Dashboard → Deployments → Click deployment → "Runtime Logs"
- See function logs (if using serverless)

### Rollback if Needed

**Vercel**:
1. Dashboard → Deployments
2. Find last working deployment
3. Click "..." → "Promote to Production"

**Render**:
1. Dashboard → Your service → "Events"
2. Find last working deployment
3. Click "Rollback"

---

## 📞 Get Help

**Something broken?**

1. Check `VERCEL_TROUBLESHOOTING.md` for common issues
2. Check `DEPLOYMENT_FAQ.md` for answers
3. Open issue on GitHub with:
   - Screenshot of error
   - Browser console output
   - Which step failed

**Documentation**:
- `DEPLOYMENT_GUIDE.md` - Full guide
- `RENDER_FREE_TIER_SOLUTIONS.md` - Handle sleep/limits
- `HOSTING_COMPARISON.md` - Alternative platforms

---

## 📋 Quick Checklist

- [ ] GitHub account created
- [ ] Render account created
- [ ] Vercel account created
- [ ] OpenAI API key obtained
- [ ] Code pushed to GitHub
- [ ] Backend deployed to Render
- [ ] Backend URL copied
- [ ] Frontend deployed to Vercel
- [ ] Environment variable set (`VITE_API_URL`)
- [ ] CORS updated in backend
- [ ] Changes pushed to GitHub
- [ ] Both services show "Live"
- [ ] Frontend URL tested
- [ ] Backend `/health` tested
- [ ] Full app tested

---

**Total Time**: ~20 minutes
**Total Cost**: $0/month (or $7/month for production)

**You're done! 🎉**

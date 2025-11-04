# ✅ Vercel Deployment Checklist

Quick reference for deploying EasyGrant to Vercel (frontend-only, recommended approach).

## Prerequisites

- [ ] GitHub account created
- [ ] Vercel account created (free): https://vercel.com
- [ ] Backend already deployed to Render
- [ ] Backend URL obtained: `https://easygrant-XXXX.onrender.com`
- [ ] OpenAI API key ready

---

## 🚀 Deployment Steps (5 minutes)

### 1. Push to GitHub
```powershell
cd C:\Users\hello\Documents\Projects\EasyGrant
git add .
git commit -m "Deploy to Vercel"
git push origin main
```

### 2. Connect Vercel to GitHub
- [ ] Login to https://vercel.com
- [ ] Click **"Add New Project"**
- [ ] Select **"Import Git Repository"**
- [ ] Choose your `EasyGrant` repo

### 3. Configure Build Settings
- [ ] **Framework Preset**: `Vite`
- [ ] **Root Directory**: `frontend`
- [ ] **Build Command**: `npm run build`
- [ ] **Output Directory**: `dist`
- [ ] **Install Command**: `npm install` (auto-detected)

### 4. Set Environment Variable
- [ ] Click **"Environment Variables"**
- [ ] Add variable:
  - **Key**: `VITE_API_URL`
  - **Value**: `https://easygrant-XXXX.onrender.com` (your Render URL)
  - **Environments**: All (Production, Preview, Development)

### 5. Deploy
- [ ] Click **"Deploy"**
- [ ] Wait 2-3 minutes for build to complete
- [ ] Copy your Vercel URL: `https://easygrant-USERNAME.vercel.app`

### 6. Update Backend CORS
- [ ] Edit `backend/src/main.py`
- [ ] Add Vercel URL to `CORS_ORIGINS`:
  ```python
  CORS_ORIGINS = [
      "http://localhost:5173",
      "https://easygrant-USERNAME.vercel.app",  # Your URL
      "https://easygrant-*.vercel.app",  # Preview deployments
  ]
  ```
- [ ] Commit and push:
  ```powershell
  git add backend/src/main.py
  git commit -m "Add Vercel CORS"
  git push
  ```
- [ ] Wait for Render to auto-deploy (~2 min)

### 7. Test Your App
- [ ] Open `https://easygrant-USERNAME.vercel.app`
- [ ] Create a session (should work)
- [ ] Upload a document (should work)
- [ ] Check browser console for errors (should be none)

---

## 🔍 Verification

Test these URLs:

- [ ] Frontend: `https://easygrant-USERNAME.vercel.app` → Shows UI
- [ ] Backend: `https://easygrant-XXXX.onrender.com/health` → Returns `{"status":"healthy"}`
- [ ] API Docs: `https://easygrant-XXXX.onrender.com/docs` → Shows Swagger UI

---

## 📊 Check Free Tier Status

### Vercel Dashboard
- [ ] Go to: https://vercel.com/dashboard
- [ ] Click on your project
- [ ] Check **Usage** tab
  - Bandwidth: `< 100 GB/month` ✅
  - Builds: Unlimited ✅

### Render Dashboard
- [ ] Go to: https://dashboard.render.com
- [ ] Click on your service
- [ ] Check metrics:
  - RAM: `< 512 MB` ✅
  - Disk: `< 1 GB` ✅

---

## 🐛 Common Issues

### ❌ Frontend shows blank page
**Fix**: Check browser console for errors. Likely API URL is wrong.
```powershell
# In Vercel dashboard: Settings → Environment Variables
# Update VITE_API_URL and redeploy
```

### ❌ CORS errors in browser
**Fix**: Backend CORS not configured.
```powershell
# Add Vercel URL to CORS_ORIGINS in backend/src/main.py
# Push to GitHub → Render auto-deploys
```

### ❌ Backend returns 500 error
**Fix**: Check Render logs for errors.
```
# Render dashboard → Logs tab
# Look for Python errors
```

### ❌ Build fails on Vercel
**Fix**: Check build logs.
```
Common causes:
1. Wrong root directory (should be "frontend")
2. Missing package.json dependencies
3. Syntax errors in code
```

---

## 🔄 Continuous Deployment

Once set up, every push to `main` triggers:

1. **Vercel**: Auto-builds and deploys frontend (1-2 min)
2. **Render**: Auto-builds and deploys backend (5-10 min)

Push to feature branches creates preview deployments on Vercel!

---

## 💡 Pro Tips

### Preview Deployments
Every pull request gets a preview URL:
- `https://easygrant-git-BRANCH-USERNAME.vercel.app`
- Great for testing before merging to main

### Environment-Specific Configs
Set different API URLs per environment:
- Production: Your Render URL
- Preview: Different backend for testing
- Development: `http://localhost:8000`

### Custom Domain
After deployment, add your domain:
1. Vercel → Project Settings → Domains
2. Add domain (e.g., `easygrant.com`)
3. Update DNS records
4. SSL auto-configured ✅

---

## 📈 Next Steps

- [ ] Set up monitoring/analytics
- [ ] Configure custom domain (optional)
- [ ] Enable Vercel Analytics (free)
- [ ] Set up GitHub Actions for tests (optional)
- [ ] Add status badge to README

---

## 🆘 Get Help

- **Vercel Docs**: https://vercel.com/docs
- **Render Docs**: https://render.com/docs
- **Project Issues**: https://github.com/YOUR_USERNAME/EasyGrant/issues

---

**Total Time**: ~10 minutes for initial setup, then automatic deployments! 🎉

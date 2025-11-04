# ⚡ Vercel Quick Start - 5 Minutes to Deploy

The absolute fastest way to get EasyGrant frontend on Vercel.

## Prerequisites (2 minutes)

1. **Deploy backend to Render first**
   - Follow: `DEPLOYMENT_GUIDE.md` Step 2
   - Get your backend URL: `https://easygrant-XXXX.onrender.com`

2. **Push code to GitHub**
   ```powershell
   cd C:\Users\hello\Documents\Projects\EasyGrant
   git add .
   git commit -m "Deploy to Vercel"
   git push origin main
   ```

## Deploy to Vercel (3 minutes)

### 1. Go to Vercel
Visit: https://vercel.com → Sign in with GitHub

### 2. Import Project
Click **"Add New Project"** → Select `EasyGrant` repo

### 3. Configure (Copy-Paste This)

```
Framework Preset: Vite
Root Directory: frontend
Build Command: npm run build
Output Directory: dist
Install Command: npm install
```

### 4. Add Environment Variable

Click **"Environment Variables"** → Add:

```
VITE_API_URL = https://easygrant-XXXX.onrender.com
```
*(Replace XXXX with your Render service ID)*

Select: ☑️ Production ☑️ Preview ☑️ Development

### 5. Deploy

Click **"Deploy"** → Wait 2-3 minutes → Done! 🎉

## Update Backend CORS (1 minute)

Copy your Vercel URL, then:

```powershell
# Edit backend/src/main.py
# Add your Vercel URL to CORS_ORIGINS:
```

```python
CORS_ORIGINS = [
    "http://localhost:5173",
    "https://YOUR-PROJECT.vercel.app",  # ← Add this
    "https://YOUR-PROJECT-*.vercel.app",  # ← And this
]
```

```powershell
# Commit and push
git add backend/src/main.py
git commit -m "Add Vercel CORS"
git push
```

Render auto-deploys in ~2 minutes.

## Test It

Open: `https://YOUR-PROJECT.vercel.app`

✅ Should see EasyGrant UI
✅ Can create session
✅ Can upload files
✅ No CORS errors in browser console

## Done! 🎉

**Your URLs:**
- Frontend: `https://YOUR-PROJECT.vercel.app`
- Backend: `https://easygrant-XXXX.onrender.com/docs`

---

## Next Time

Every `git push` to main = auto-deploy! No manual steps needed.

---

## Troubleshooting

**Blank page?**
→ Check VITE_API_URL in Vercel dashboard → Settings → Environment Variables

**CORS errors?**
→ Add Vercel URL to backend CORS_ORIGINS and push

**Build fails?**
→ Check Root Directory is set to `frontend`

---

**Full Docs**: See `VERCEL_DEPLOYMENT.md` for detailed explanations

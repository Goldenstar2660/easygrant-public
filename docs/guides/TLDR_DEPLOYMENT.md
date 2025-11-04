# ⚡ Ultra-Quick Deployment (TL;DR)

For experienced developers who just need the commands.

## Prerequisites
- GitHub, Render, Vercel accounts
- OpenAI API key

## Deploy (15 minutes)

### 1. Push to GitHub
```powershell
cd C:\Users\hello\Documents\Projects\EasyGrant
git init
git add .
git commit -m "Deploy"
git remote add origin https://github.com/YOUR_USERNAME/EasyGrant.git
git branch -M main
git push -u origin main
```

### 2. Render (Backend)
1. https://dashboard.render.com → New + → Web Service
2. Connect GitHub repo
3. Click "Apply" (uses `render.yaml`)
4. Add env var: `OPENAI_API_KEY=sk-...`
5. Deploy (wait 5-10 min)
6. Copy URL: `https://easygrant-XXXX.onrender.com`

### 3. Vercel (Frontend)
1. https://vercel.com/dashboard → Add New → Project
2. Import `EasyGrant` repo
3. Settings:
   - Framework: `Vite`
   - Root: `frontend`
   - Build: `npm run build`
   - Output: `dist`
4. Env var: `VITE_API_URL=https://easygrant-XXXX.onrender.com`
5. Deploy (wait 2-3 min)
6. Copy URL: `https://easygrant-USERNAME.vercel.app`

### 4. Update CORS
Edit `backend/src/main.py`:
```python
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://easygrant-USERNAME.vercel.app",  # Add this
    "https://easygrant-*-USERNAME.vercel.app",  # Add this
]
```

```powershell
git add backend/src/main.py
git commit -m "Add CORS"
git push
```

Wait 2 min for Render auto-deploy.

### 5. Test
- Frontend: `https://easygrant-USERNAME.vercel.app`
- Backend: `https://easygrant-XXXX.onrender.com/health`
- API Docs: `https://easygrant-XXXX.onrender.com/docs`

## Done! 🎉

**Important**: Render free tier sleeps after 15min (30s wake), 750 hrs/month limit.

For production: Upgrade Render to Starter ($7/mo) for 24/7 uptime.

---

See `SIMPLE_DEPLOYMENT_GUIDE.md` for detailed steps.

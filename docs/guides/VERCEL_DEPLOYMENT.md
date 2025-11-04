# 🚀 Deploy EasyGrant to Vercel for FREE

This guide shows you how to deploy **EasyGrant** completely for free using **Vercel** for both frontend and backend. Vercel offers serverless functions that can host your FastAPI backend alongside your React frontend.

## 📋 What You'll Get

- ✅ **Frontend**: React + Vite app hosted on Vercel's edge network
- ✅ **Backend**: FastAPI serverless functions on Vercel
- ✅ **Free SSL**: Automatic HTTPS
- ✅ **Global CDN**: Fast load times worldwide
- ✅ **Auto-deployment**: Push to GitHub = auto-deploy
- ✅ **No Cold Starts**: Unlike Render's free tier, Vercel doesn't sleep

## ⚠️ Important Limitations

**Vercel's Free Tier has constraints that affect this application:**

1. **Serverless Function Limits**:
   - Max 10-second execution time (paid: 60s)
   - Max 50MB function size
   - File system is **read-only** (except `/tmp`)

2. **Storage Issues**:
   - Your app needs persistent storage for:
     - Uploaded documents (`/data/uploads`)
     - Vector database (`/vector`)
   - Serverless functions **cannot persist files** between requests

3. **Recommended Architecture**:
   - **Frontend on Vercel** (perfect fit)
   - **Backend on Render** (free tier supports persistent storage)
   - This is documented in `DEPLOYMENT_GUIDE.md`

---

## 🎯 Option 1: Frontend-Only on Vercel (RECOMMENDED)

Deploy just the frontend to Vercel, and backend to Render.

### Step 1: Deploy Backend to Render

Follow the existing `DEPLOYMENT_GUIDE.md` to deploy backend to Render first. You'll get a URL like:
```
https://easygrant-XXXX.onrender.com
```

### Step 2: Deploy Frontend to Vercel

#### A. Push Code to GitHub

```powershell
# Navigate to your project
cd C:\Users\hello\Documents\Projects\EasyGrant

# Initialize git (if not done)
git init
git add .
git commit -m "Ready for Vercel deployment"

# Create new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/EasyGrant.git
git branch -M main
git push -u origin main
```

#### B. Deploy to Vercel

1. **Sign up/Login** at https://vercel.com
2. Click **"Add New Project"**
3. **Import your GitHub repository**
4. **Configure Build Settings**:
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

5. **Add Environment Variable**:
   - Click **"Environment Variables"**
   - Add variable:
     - **Name**: `VITE_API_URL`
     - **Value**: `https://easygrant-XXXX.onrender.com` (your Render backend URL)
     - **Environments**: Production, Preview, Development (select all)

6. Click **"Deploy"**

#### C. Wait for Deployment (2-3 minutes)

Vercel will:
- Install dependencies
- Build your React app
- Deploy to global CDN
- Provide you a URL: `https://easygrant.vercel.app`

#### D. Update Backend CORS

After frontend is deployed, update backend to allow Vercel domain:

1. **Edit** `backend/src/main.py`:

```python
CORS_ORIGINS = [
    "http://localhost:5173",  # Local dev
    "http://localhost:3000",
    "https://easygrant.vercel.app",  # Your Vercel URL
    "https://easygrant-*.vercel.app",  # Preview deployments
]
```

2. **Commit and push**:

```powershell
git add backend/src/main.py
git commit -m "Add Vercel CORS origins"
git push
```

Render will auto-deploy the backend update!

---

## 🎯 Option 2: Full-Stack on Vercel (Advanced)

⚠️ **Not recommended for production** due to storage limitations, but possible for demo/testing.

### Required Changes

To deploy the full app on Vercel, you need to:

1. **Convert backend to serverless functions**
2. **Use external storage** (S3, Supabase, etc.) for file uploads
3. **Use hosted vector DB** (Pinecone, Weaviate Cloud, etc.)

### File Structure for Vercel

```
EasyGrant/
├── api/                    # Backend as serverless functions
│   └── index.py           # Main FastAPI app
├── frontend/
│   └── ... (unchanged)
├── vercel.json            # Vercel configuration
└── requirements.txt       # Python dependencies
```

### Step 1: Create `vercel.json`

Create this file in your project root:

```json
{
  "version": 2,
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "frontend/dist"
      }
    },
    {
      "src": "api/index.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "api/index.py"
    },
    {
      "src": "/(.*)",
      "dest": "frontend/dist/$1"
    }
  ],
  "env": {
    "OPENAI_API_KEY": "@openai-api-key"
  },
  "build": {
    "env": {
      "VITE_API_URL": ""
    }
  }
}
```

### Step 2: Create `api/index.py`

Move your FastAPI app to work as serverless:

```python
"""
Serverless FastAPI wrapper for Vercel
"""
from fastapi import FastAPI
from mangum import Mangum
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import your main app
from backend.src.main import app

# Wrap with Mangum for serverless
handler = Mangum(app)
```

### Step 3: Update Dependencies

Add to `requirements.txt`:

```txt
mangum>=0.17.0  # ASGI adapter for serverless
```

### Step 4: Configure External Storage

Since Vercel functions can't persist files, you need external storage:

#### Option A: Supabase (Free Tier Available)

```python
# backend/src/services/storage_service.py
from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

def upload_file(file_data, filename, session_id):
    """Upload file to Supabase Storage"""
    path = f"{session_id}/{filename}"
    supabase.storage.from_("uploads").upload(path, file_data)
    return path
```

#### Option B: Cloudflare R2 / AWS S3

Similar setup with boto3 or cloudflare SDK.

### Step 5: Configure Hosted Vector DB

Replace local ChromaDB with cloud service:

#### Option A: Pinecone (Free Tier: 1 index, 100K vectors)

```python
# backend/src/services/vector_store.py
import pinecone
import os

pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment=os.getenv("PINECONE_ENV")
)

index = pinecone.Index("easygrant")
```

#### Option B: Weaviate Cloud

Free tier available with hosted instance.

### Step 6: Deploy to Vercel

```powershell
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel --prod
```

### Step 7: Set Environment Variables

In Vercel dashboard, add:

- `OPENAI_API_KEY`
- `SUPABASE_URL` (if using Supabase)
- `SUPABASE_KEY`
- `PINECONE_API_KEY` (if using Pinecone)
- `PINECONE_ENV`

---

## 🆚 Comparison: Vercel vs Render

| Feature | Vercel (Frontend) | Render (Backend) | Vercel (Full-Stack) |
|---------|-------------------|------------------|---------------------|
| **Cost** | Free ✅ | Free ✅ | Free ✅ |
| **Storage** | Static only | 1GB persistent ✅ | Read-only ⚠️ |
| **Timeout** | - | No limit ✅ | 10s max ⚠️ |
| **Cold Start** | None ✅ | 30s on free tier | None ✅ |
| **Setup Complexity** | Easy ✅ | Easy ✅ | Complex ⚠️ |
| **Best For** | Frontend | Backend + DB | Simple APIs only |

---

## 📊 Free Tier Limits

### Vercel Free Tier:

- ✅ **100GB bandwidth/month**
- ✅ **Unlimited deployments**
- ✅ **Automatic SSL**
- ✅ **DDoS protection**
- ✅ **Analytics (limited)**
- ⚠️ **10-second function timeout**
- ⚠️ **No persistent storage**

### When to Upgrade:

- Need longer function timeouts (upgrade to Pro: $20/month)
- Need more bandwidth (>100GB/month)
- Want advanced analytics
- Need preview deployment limits increased

---

## 🔧 Custom Domain (Optional)

After deployment, add your own domain:

1. Go to **Project Settings** → **Domains**
2. Click **"Add Domain"**
3. Enter your domain (e.g., `easygrant.com`)
4. Follow DNS configuration instructions
5. Vercel auto-provisions SSL certificate

---

## 🔄 Continuous Deployment

Once connected to GitHub:

- **Push to `main` branch** = auto-deploy to production
- **Push to other branches** = create preview deployments
- **Pull requests** = automatic preview links

Configure in **Project Settings** → **Git**.

---

## 🐛 Troubleshooting

### Frontend Can't Connect to Backend

**Check**:
1. `VITE_API_URL` environment variable is set correctly
2. No trailing slash in API URL
3. Backend CORS includes your Vercel domain

**Fix**:
```powershell
# In Vercel dashboard
# Settings → Environment Variables
# Update VITE_API_URL to: https://easygrant-xxxx.onrender.com
# Then redeploy
```

### Build Fails

**Common causes**:
1. Wrong root directory (should be `frontend`)
2. Missing dependencies in `package.json`
3. Environment variables not set

**Fix**:
```powershell
# Test build locally first
cd frontend
npm install
npm run build

# If successful, commit and push
```

### Environment Variables Not Working

**Vite requires variables to start with `VITE_`**:

❌ Wrong: `API_URL`
✅ Correct: `VITE_API_URL`

Access in code:
```javascript
const apiUrl = import.meta.env.VITE_API_URL;
```

### Preview Deployments Show Old Version

Vercel caches builds. To force rebuild:

1. Go to **Deployments**
2. Click **"..."** on deployment
3. Click **"Redeploy"**

---

## 📈 Monitoring

### Vercel Dashboard

Access at https://vercel.com/dashboard

- **Analytics**: View page views, performance metrics
- **Logs**: Real-time function logs (Runtime Logs)
- **Deployments**: See all builds and previews
- **Speed Insights**: Core Web Vitals (Pro tier)

### View Logs

1. Go to **Project** → **Deployments**
2. Click on deployment
3. Click **"Runtime Logs"** tab

---

## 🔒 Security Checklist

Before going live:

- [ ] All API keys in environment variables (not in code)
- [ ] CORS configured for production domains only
- [ ] `.env` files in `.gitignore`
- [ ] Rate limiting enabled on backend
- [ ] Content Security Policy headers set
- [ ] HTTPS enforced (automatic on Vercel)

---

## 🎓 Next Steps

After successful deployment:

1. **Test the app** thoroughly on production
2. **Monitor usage** to stay within free tier limits
3. **Set up alerts** in Vercel dashboard
4. **Configure custom domain** (optional)
5. **Enable Web Analytics** in Vercel settings

---

## 📚 Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Vite Deployment Guide](https://vitejs.dev/guide/static-deploy.html)
- [FastAPI on Vercel](https://vercel.com/docs/frameworks/fastapi)
- [Environment Variables Guide](https://vercel.com/docs/concepts/projects/environment-variables)

---

## 🆘 Need Help?

- Vercel Support: https://vercel.com/support
- Vercel Discord: https://vercel.com/discord
- Check existing `DEPLOYMENT_GUIDE.md` for Render setup

---

**Recommended Approach**: Use Vercel for frontend + Render for backend (as documented in `DEPLOYMENT_GUIDE.md`). This gives you the best of both platforms for free!

# 🔧 Vercel Deployment Troubleshooting

Common issues when deploying EasyGrant to Vercel and how to fix them.

---

## 🚨 Build Errors

### Error: "Build failed - Cannot find module 'react'"

**Cause**: Wrong root directory or missing dependencies.

**Fix**:
1. Vercel dashboard → Settings → General
2. Check **Root Directory**: Must be `frontend`
3. Check **Install Command**: `npm install` (or auto)
4. Click **Save** → **Redeploy**

---

### Error: "VITE_API_URL is not defined"

**Cause**: Environment variable not set or misspelled.

**Fix**:
1. Vercel dashboard → Settings → Environment Variables
2. Add variable:
   - Name: `VITE_API_URL` (must start with `VITE_`)
   - Value: `https://easygrant-xxxx.onrender.com`
   - Environments: ✅ Production ✅ Preview ✅ Development
3. Deployments → Latest → **Redeploy**

**Important**: Vite requires env vars to start with `VITE_` prefix!

---

### Error: "Build exceeded maximum duration"

**Cause**: Build taking too long (free tier: 45 minutes max).

**Fix**:
1. Check `package.json` for unnecessary build steps
2. Remove large dependencies if possible
3. Usually not an issue with Vite (builds in 1-2 min)

If persists:
```powershell
# Test build locally
cd frontend
npm install
npm run build

# Should complete in <2 minutes
```

---

## 🌐 CORS Errors

### Error: "Access to fetch blocked by CORS policy"

**Symptom**: Browser console shows:
```
Access to fetch at 'https://easygrant-xxxx.onrender.com/api/...' 
from origin 'https://easygrant.vercel.app' has been blocked by CORS policy
```

**Cause**: Backend doesn't allow Vercel domain.

**Fix**:
1. Edit `backend/src/main.py`:

```python
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://easygrant.vercel.app",          # Your domain
    "https://easygrant-*.vercel.app",        # Preview deployments
]
```

2. Commit and push:
```powershell
git add backend/src/main.py
git commit -m "Add Vercel to CORS"
git push
```

3. Wait for Render to auto-deploy (~2 min)

4. Hard refresh browser: `Ctrl + Shift + R`

---

### Error: "CORS error on localhost but not production"

**Cause**: Trying to test production frontend with local backend.

**Fix**: Don't mix environments!

**Local Development**:
```
Frontend: http://localhost:5173
Backend: http://localhost:8000
```

**Production**:
```
Frontend: https://easygrant.vercel.app
Backend: https://easygrant-xxxx.onrender.com
```

To test production frontend locally:
```powershell
# Build and preview
cd frontend
npm run build
npm run preview
```

---

## 📡 API Connection Issues

### Error: "Failed to fetch" or "Network Error"

**Symptoms**:
- Browser console shows network errors
- API calls fail immediately
- No data loading

**Debug Steps**:

1. **Check API URL**:
```javascript
// In browser console
console.log(import.meta.env.VITE_API_URL)
// Should show: https://easygrant-xxxx.onrender.com
```

2. **Test backend directly**:
   - Open: `https://easygrant-xxxx.onrender.com/health`
   - Should return: `{"status":"healthy"}`

3. **Check environment variable**:
   - Vercel dashboard → Settings → Environment Variables
   - Verify `VITE_API_URL` is set correctly
   - No trailing slash: ❌ `https://...com/` ✅ `https://...com`

4. **Redeploy if changed**:
   - Deployments → Latest → **Redeploy**

---

### Error: Backend returns 404 for API routes

**Symptoms**:
- `GET /api/session/create` → 404 Not Found
- Backend health check works
- All API routes fail

**Cause**: Wrong API base URL or backend not running.

**Fix**:

1. **Check backend is running**:
   - Render dashboard → Your service
   - Status should be: 🟢 Live
   - If 🔴 Failed: Check Logs tab

2. **Verify API URL format**:
   ```
   ✅ Correct: https://easygrant-xxxx.onrender.com
   ❌ Wrong: https://easygrant-xxxx.onrender.com/
   ❌ Wrong: http://easygrant-xxxx.onrender.com (not HTTPS)
   ```

3. **Check frontend API client**:
   - Open `frontend/src/services/api.js`
   - Should use `import.meta.env.VITE_API_URL`

---

## 🐌 Performance Issues

### Issue: "First load is very slow (30+ seconds)"

**Cause**: Render free tier cold start.

**Expected Behavior**:
- First request after 15min idle: ~30 seconds
- Subsequent requests: Fast (<100ms)

**Solutions**:

**Option 1: Accept it** (free tier limitation)

**Option 2: Keep backend warm** (hacky):
```javascript
// Add to frontend - pings backend every 10 minutes
useEffect(() => {
  const interval = setInterval(() => {
    fetch('https://easygrant-xxxx.onrender.com/health')
  }, 10 * 60 * 1000) // 10 minutes
  
  return () => clearInterval(interval)
}, [])
```

**Option 3: Upgrade Render** ($7/mo):
- Render dashboard → Upgrade to Starter
- Removes cold starts

---

### Issue: "Frontend loads slowly"

**Unlikely** - Vercel uses global CDN.

**Debug**:
1. Test with DevTools Network tab
2. Check asset sizes
3. Enable Vercel Analytics (Settings → Analytics)

**Optimize**:
```powershell
# Check build size
cd frontend
npm run build

# Should be <5MB total
```

---

## 📄 Blank Page Issues

### Issue: "Vercel URL shows blank white page"

**Symptoms**:
- No errors in Network tab
- Just empty page

**Debug**:

1. **Open browser console** (F12)
   - Look for JavaScript errors
   - Look for CORS errors

2. **Check if React loaded**:
```javascript
// In console
document.getElementById('root')
// Should show React root element
```

3. **Common causes**:

**a) Wrong build output**:
```
Vercel Settings → General
Output Directory: dist  ✅
                  build ❌ (wrong for Vite)
```

**b) Missing environment variables**:
- App may crash if API URL is undefined
- Add fallback in code:
```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

**c) JavaScript error on load**:
- Check browser console
- Fix error in code
- Commit and push

---

## 🔐 Environment Variable Issues

### Issue: "Environment variables not updating"

**Cause**: Vercel caches builds.

**Fix**:
1. Update variable in dashboard
2. **Must redeploy** for changes to take effect
3. Deployments → Latest → **Redeploy**

Or force rebuild:
```powershell
git commit --allow-empty -m "Force rebuild"
git push
```

---

### Issue: "Can't access env vars in code"

**Remember**:
- ✅ `import.meta.env.VITE_API_URL` (Vite)
- ❌ `process.env.VITE_API_URL` (Node.js, won't work in browser)

**Only variables starting with `VITE_` are exposed to browser!**

---

## 🔄 Deployment Issues

### Issue: "Push to GitHub but no auto-deploy"

**Cause**: Auto-deploy not configured.

**Fix**:
1. Vercel dashboard → Settings → Git
2. Check **Production Branch**: `main` (or your branch)
3. Enable **Auto-deploy** toggle

---

### Issue: "Preview deployment created but production not updated"

**Cause**: You pushed to a feature branch, not `main`.

**Check**:
```powershell
git branch
# Should show: * main
```

**Fix**:
```powershell
# Merge feature branch to main
git checkout main
git merge your-feature-branch
git push origin main
```

---

## 🔍 Debugging Tools

### Vercel Runtime Logs

1. Vercel dashboard → Your project
2. Deployments → Click on deployment
3. **Runtime Logs** tab
4. See real-time function logs

**Not useful for frontend** (static files), but helpful for serverless functions.

---

### Browser DevTools

**Network Tab**:
- See all API requests
- Check response status codes
- View response bodies

**Console Tab**:
- See JavaScript errors
- Check environment variables:
  ```javascript
  console.log(import.meta.env)
  ```

**Application Tab**:
- Check localStorage
- View cookies
- Inspect service workers

---

### Test API Directly

**Using browser**:
```
https://easygrant-xxxx.onrender.com/docs
```
Opens Swagger UI - test endpoints directly.

**Using PowerShell**:
```powershell
# Test health endpoint
curl https://easygrant-xxxx.onrender.com/health

# Test API endpoint
curl -X POST https://easygrant-xxxx.onrender.com/api/session/create
```

---

## 🚑 Emergency Fixes

### "Everything is broken, need to rollback"

**Rollback to previous deployment**:

1. Vercel dashboard → Deployments
2. Find last working deployment (green checkmark)
3. Click **"..."** → **"Promote to Production"**

Instant rollback! 🎉

---

### "Backend is down, can't fix immediately"

**Temporary fix - point to local backend**:

1. Vercel dashboard → Settings → Environment Variables
2. Update `VITE_API_URL` to your local tunnel:
   - Use ngrok: `https://abc123.ngrok.io`
   - Or Cloudflare Tunnel
3. Redeploy

**Not recommended for production**, but works for emergencies.

---

## 📊 Monitoring

### Check if services are up

**Frontend (Vercel)**:
```
https://easygrant.vercel.app
Should load immediately
```

**Backend (Render)**:
```
https://easygrant-xxxx.onrender.com/health
Should return: {"status":"healthy"}
```

**If backend is sleeping**:
- First request takes ~30 seconds
- Check again after 1 minute

---

### Set up alerts

**Vercel**:
- Deployment notifications via email
- Settings → Notifications

**Render**:
- Health check failures via email
- Dashboard → Notifications

**External monitoring** (free):
- UptimeRobot: https://uptimerobot.com
- Ping backend every 5 minutes
- Email alert if down

---

## 🆘 Still Not Working?

### Checklist

- [ ] Root directory set to `frontend`
- [ ] Build command is `npm run build`
- [ ] Output directory is `dist`
- [ ] `VITE_API_URL` environment variable set
- [ ] Backend URL has no trailing slash
- [ ] Backend is running (check Render dashboard)
- [ ] CORS configured with Vercel domain
- [ ] No JavaScript errors in browser console
- [ ] Tried hard refresh (`Ctrl + Shift + R`)
- [ ] Tried redeploying

### Get Help

**Vercel Support**:
- Free tier: Community support only
- https://vercel.com/support

**Render Support**:
- Free tier: Community support
- https://render.com/docs

**GitHub Issues**:
- Open issue with:
  - Screenshot of error
  - Browser console output
  - Link to deployment
  - Environment (browser, OS)

---

## 💡 Pro Tips

### Enable Verbose Logging

**Frontend** (temporary):
```javascript
// Add to frontend/src/services/api.js
apiClient.interceptors.request.use(request => {
  console.log('🚀 Request:', request)
  return request
})

apiClient.interceptors.response.use(
  response => {
    console.log('✅ Response:', response)
    return response
  },
  error => {
    console.error('❌ Error:', error)
    return Promise.reject(error)
  }
)
```

**Backend**:
- Check Render logs in real-time
- Dashboard → Logs tab

### Test Production Locally

```powershell
# Set production API URL locally
cd frontend
$env:VITE_API_URL="https://easygrant-xxxx.onrender.com"
npm run dev

# Browse to http://localhost:5173
# Now using production backend!
```

### Compare Environments

| Environment | Frontend | Backend |
|-------------|----------|---------|
| Local Dev | localhost:5173 | localhost:8000 |
| Production | vercel.app | onrender.com |
| Test Prod Locally | localhost:5173 | onrender.com |

---

**Updated**: October 26, 2025

# Frontend Testing Guide

## 🧪 Testing Options

You have two options for testing the frontend:

1. **Local Testing** (Recommended for development)
2. **Render Deployment Testing** (For production verification)

---

## Option 1: Local Testing (Recommended)

### Prerequisites

- Node.js 18+ installed
- Backend running on `http://localhost:8000`
- OpenAI API key configured in `backend/config.yaml`

### Step 1: Start the Backend Server

Open a terminal and run:

```bash
# From project root
cd C:\Users\hello\Documents\Projects\EasyGrant

# Set OpenAI API key (if not in config.yaml)
$env:OPENAI_API_KEY="your-api-key-here"

# Start FastAPI backend
uvicorn backend.src.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify Backend**:
- Open browser: http://localhost:8000/docs
- You should see FastAPI Swagger UI with endpoints:
  - `/api/session/create`
  - `/api/upload/funding-call`
  - `/api/upload/supporting-docs`
  - `/api/upload/status`

### Step 2: Install Frontend Dependencies

Open a **new terminal** (keep backend running):

```bash
cd C:\Users\hello\Documents\Projects\EasyGrant\frontend

# Install dependencies
npm install
```

**Expected Output**:
```
added 215 packages, and audited 216 packages in 15s
```

### Step 3: Create Environment File

Create `.env` file in the `frontend/` directory:

```bash
# Create .env file
Copy-Item .env.example .env

# Or manually create with this content:
# VITE_API_URL=http://localhost:8000
```

**Verify `.env` file**:
```bash
cat .env
# Should show: VITE_API_URL=http://localhost:8000
```

### Step 4: Start Frontend Dev Server

```bash
# From frontend directory
npm run dev
```

**Expected Output**:
```
  VITE v5.0.0  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

### Step 5: Open Browser and Test

**Open**: http://localhost:5173/

You should see:
- **Header**: "🎯 EasyGrant Smart Proposal Assistant"
- **Upload Panel**: Two sections (Funding Call + Supporting Docs)
- **Quota Display**: "0.0 / 50 MB"

### Step 6: Manual Test Checklist

#### Test 1: Funding Call Upload ✓

1. **Prepare test PDF**:
   - Download any PDF (e.g., research paper, report)
   - Ensure it's under 10MB

2. **Upload via drag-and-drop**:
   - Drag PDF file over "Funding Call" dropzone
   - Dropzone should highlight with green border
   - Drop file → file preview should appear

3. **Click "Upload & Index Funding Call"**:
   - Progress bar should animate 0-100%
   - Message changes: "Uploading... 50%" → "Indexing document..."
   - Success message: "✓ Funding call uploaded! X chunks indexed"
   - Quota should update (e.g., "2.5 / 50 MB")

4. **Verify backend**:
   - Check terminal running backend
   - Should see POST requests to `/api/upload/funding-call`
   - No errors in logs

#### Test 2: Supporting Documents Upload ✓

1. **Prepare 2-3 test files**:
   - Mix of PDFs and DOCX files
   - Each under 10MB

2. **Upload via file picker**:
   - Click "browse" link in Supporting Docs dropzone
   - Select multiple files (Ctrl+Click or Cmd+Click)
   - File list should appear with names and sizes

3. **Remove a file** (optional):
   - Click "×" button on any file
   - File should be removed from list

4. **Click "Upload & Index X Documents"**:
   - Progress bar animates
   - Success message: "X documents uploaded! Y total chunks indexed"
   - Uploaded summary appears with chunk counts

#### Test 3: Quota Display ✓

1. **Verify quota updates**:
   - After each upload, quota should increase
   - Progress bar should fill proportionally
   - File count should increment

2. **Test quota limits**:
   - Upload files until total approaches 50MB
   - Try uploading a file that would exceed 50MB
   - Should see error toast: "Upload would exceed 50MB quota"

#### Test 4: File Validation ✓

1. **Test invalid file type**:
   - Try uploading .txt, .jpg, or .zip file
   - Should see error toast: "Invalid file type..."

2. **Test oversized file**:
   - Try uploading PDF > 10MB
   - Should see error toast: "File too large. Maximum size: 10MB"

3. **Test too many files**:
   - Try uploading 6 supporting documents
   - Should see error toast: "Maximum 5 supporting documents allowed"

#### Test 5: Error Handling ✓

1. **Test network error** (backend not running):
   - Stop backend server (Ctrl+C in backend terminal)
   - Try uploading a file
   - Should see error toast: "Network error. Please check your connection."

2. **Test backend error**:
   - Restart backend without OpenAI API key
   - Upload a file
   - Should see error toast with server error message

### Step 7: Check Browser Console

Open DevTools (F12) → Console tab:

**Expected**:
- No red error messages
- Should see API requests: `POST /api/session/create`, `POST /api/upload/funding-call`
- Responses should have status 200

**Common Issues**:
- CORS errors → Check backend CORS settings in `main.py`
- 404 errors → Check API base URL in `.env`
- Network errors → Ensure backend is running on port 8000

---

## Option 2: Render Deployment Testing

### Prerequisites

- Backend deployed to Render
- Render service URL (e.g., `https://easygrant-xyz.onrender.com`)

### Step 1: Update Frontend Environment

```bash
cd C:\Users\hello\Documents\Projects\EasyGrant\frontend

# Create .env with Render URL
echo "VITE_API_URL=https://easygrant-xyz.onrender.com" > .env
```

**Replace** `easygrant-xyz` with your actual Render service name.

### Step 2: Build Frontend for Production

```bash
# From frontend directory
npm run build
```

**Expected Output**:
```
vite v5.0.0 building for production...
✓ 150 modules transformed.
dist/index.html                  0.45 kB │ gzip:  0.30 kB
dist/assets/index-abc123.css     5.23 kB │ gzip:  1.45 kB
dist/assets/index-xyz789.js     143.50 kB │ gzip: 46.20 kB
✓ built in 2.50s
```

### Step 3: Serve Production Build Locally

```bash
# Preview production build
npm run preview
```

**Expected Output**:
```
  ➜  Local:   http://localhost:4173/
  ➜  Network: use --host to expose
```

**Open**: http://localhost:4173/

### Step 4: Test with Render Backend

Follow the same test checklist as local testing, but:
- API calls go to Render backend (e.g., `https://easygrant-xyz.onrender.com`)
- First request may be slow (~30s) if Render service is in sleep mode
- Check Render logs for any errors

### Step 5: Deploy Frontend to Render (Optional)

You have two options for deploying frontend to Render:

#### Option A: Static Site (Recommended)

1. **Create new Static Site on Render**:
   - Go to https://dashboard.render.com
   - Click "New +" → "Static Site"
   - Connect GitHub repository
   - Set build settings:
     - **Build Command**: `cd frontend && npm install && npm run build`
     - **Publish Directory**: `frontend/dist`
     - **Environment Variable**: `VITE_API_URL=https://your-backend.onrender.com`

2. **Deploy**:
   - Click "Create Static Site"
   - Wait for build to complete (~2-3 minutes)
   - Get URL: `https://easygrant-frontend.onrender.com`

#### Option B: Serve from Backend (Simpler)

Update `backend/src/main.py` to serve static files:

```python
from fastapi.staticfiles import StaticFiles

# After CORS middleware
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
```

Then update Render build command to include frontend build:

**render.yaml**:
```yaml
buildCommand: "pip install -r backend/requirements.txt && cd frontend && npm install && npm run build"
```

This serves frontend from the same URL as backend.

---

## 🐛 Troubleshooting

### Issue: "Network error" toast

**Cause**: Frontend can't reach backend

**Solutions**:
1. Check backend is running: http://localhost:8000/docs
2. Verify `.env` has correct API URL
3. Check browser console for CORS errors
4. Ensure `main.py` has CORS middleware with correct origins

### Issue: "Failed to create session"

**Cause**: Backend not responding or session endpoint broken

**Solutions**:
1. Check backend logs for errors
2. Test session endpoint directly:
   ```bash
   curl -X POST http://localhost:8000/api/session/create
   ```
3. Verify session routes are registered in `main.py`

### Issue: Upload progress stuck at 100%

**Cause**: Indexing is taking a long time (large files)

**Solutions**:
1. Wait longer (10MB PDF can take 20-30 seconds)
2. Check backend logs for indexing progress
3. Ensure OpenAI API key is valid
4. Check network connectivity to OpenAI APIs

### Issue: "Invalid file type" for valid PDF

**Cause**: PDF is corrupted or has unusual structure

**Solutions**:
1. Try a different PDF file
2. Check file actually has PDF magic bytes:
   ```bash
   # First 4 bytes should be "%PDF"
   Get-Content test.pdf -Encoding Byte -TotalCount 4
   ```
3. Convert to standard PDF using Adobe/online converter

### Issue: CORS errors in browser console

**Error**: `Access to XMLHttpRequest blocked by CORS policy`

**Solution**: Update `backend/src/main.py`:

```python
CORS_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:4173",  # Vite preview
    "https://easygrant-frontend.onrender.com",  # Production
]
```

### Issue: 413 Request Entity Too Large

**Cause**: Nginx/reverse proxy limiting upload size

**Solution**: For Render deployment, add to `render.yaml`:

```yaml
envVars:
  - key: CLIENT_MAX_BODY_SIZE
    value: "50M"
```

---

## 📊 Expected Behavior

### Session Creation
- ✅ Auto-creates session on page load
- ✅ Displays session ID in browser console
- ✅ Shows initial quota: "0.0 / 50 MB"

### Funding Call Upload
- ✅ Accepts only PDF files
- ✅ Max 10MB per file
- ✅ Shows upload progress (0-100%)
- ✅ Shows "Indexing..." message after upload
- ✅ Displays chunk count on success
- ✅ Updates quota display

### Supporting Docs Upload
- ✅ Accepts PDF and DOCX files
- ✅ Max 5 files
- ✅ Max 10MB per file, 50MB total
- ✅ Shows file list with sizes
- ✅ Allows removing files before upload
- ✅ Shows batch upload progress
- ✅ Displays uploaded files with chunk counts

### Error Handling
- ✅ Shows toast notification for errors
- ✅ Auto-dismisses after 5 seconds
- ✅ Click "×" to dismiss manually
- ✅ Clear error messages with actionable guidance

---

## 🔍 Checking Backend Connection

### Quick Backend Health Check

```bash
# Test backend is running
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","version":"1.0.0"}
```

### Test Session Creation

```bash
# Create a session
curl -X POST http://localhost:8000/api/session/create

# Expected response:
# {
#   "session_id": "abc-123-def-456",
#   "created_at": "2025-10-26T12:00:00",
#   "quota": {"max_size_mb": 50, "max_files": 5}
# }
```

### Test File Upload (with curl)

```bash
# Upload funding call
curl -X POST http://localhost:8000/api/upload/funding-call \
  -H "X-Session-ID: your-session-id" \
  -F "file=@test.pdf"

# Expected response:
# {
#   "success": true,
#   "file_id": "xyz-789",
#   "chunk_count": 23
# }
```

---

## 📸 Screenshots (Expected UI)

### Initial State
```
┌─────────────────────────────────────────────────┐
│ 🎯 EasyGrant Smart Proposal Assistant          │
│ Upload funding call + docs → Generate proposal  │
├─────────────────────────────────────────────────┤
│ 📁 Upload Documents                             │
│ Storage: 0.0 / 50 MB [▓▓▓░░░░░░░░░░░░░░░░░]   │
├─────────────────────────────────────────────────┤
│ 1. Funding Call (Required)                      │
│ Upload the funding call PDF to extract reqs     │
│ ┌───────────────────────────────────────────┐   │
│ │        📄                                 │   │
│ │  Drag & drop PDF here, or browse         │   │
│ │        Maximum 10 MB                      │   │
│ └───────────────────────────────────────────┘   │
├─────────────────────────────────────────────────┤
│ 2. Supporting Documents (Optional)              │
│ Upload community documents (max 5, 50MB)        │
│ 0 / 5 files     0.0 / 50 MB used               │
│ ┌───────────────────────────────────────────┐   │
│ │        📚                                 │   │
│ │  Drag & drop PDF/DOCX here, or browse    │   │
│ │        Max 5 files, 10MB each             │   │
│ └───────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### After Upload
```
┌─────────────────────────────────────────────────┐
│ 📁 Upload Documents                             │
│ Storage: 12.5 / 50 MB [▓▓▓▓▓░░░░░░░░░░░░░░░]  │
├─────────────────────────────────────────────────┤
│ 1. Funding Call (Required)                      │
│ ┌───────────────────────────────────────────┐   │
│ │  ✓  Funding call uploaded!                │   │
│ │     23 chunks indexed                     │   │
│ └───────────────────────────────────────────┘   │
├─────────────────────────────────────────────────┤
│ 2. Supporting Documents (Optional)              │
│ Uploaded Documents (2):                         │
│  ✓ community-profile.pdf      12 chunks        │
│  ✓ demographics.docx           8 chunks        │
└─────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start Commands

### Local Development (Full Stack)

```bash
# Terminal 1: Start backend
cd C:\Users\hello\Documents\Projects\EasyGrant
uvicorn backend.src.main:app --reload

# Terminal 2: Start frontend
cd C:\Users\hello\Documents\Projects\EasyGrant\frontend
npm install
npm run dev

# Open browser: http://localhost:5173
```

### Production Build Test

```bash
# Build frontend
cd frontend
npm run build

# Preview production build
npm run preview

# Open browser: http://localhost:4173
```

### Backend API Testing

```bash
# Health check
curl http://localhost:8000/health

# Interactive API docs
# Open: http://localhost:8000/docs
```

---

## ✅ Success Criteria

After testing, you should be able to:

- [x] See UploadPanel UI load without errors
- [x] Create session automatically on page load
- [x] Drag & drop PDF file with visual feedback
- [x] Upload funding call with progress indicator
- [x] See "Indexing..." message during processing
- [x] Get success message with chunk count
- [x] See quota update after upload
- [x] Upload multiple supporting documents
- [x] See uploaded files list with chunk counts
- [x] Get error toast for invalid files
- [x] Get error toast when quota exceeded

---

**Need Help?**
- Check browser console (F12) for detailed errors
- Check backend logs for API errors
- Review `PHASE3_SUMMARY.md` for architecture details
- See `test_phase3_backend.py` for backend test examples

# 🧪 Quick Frontend Test Checklist

## Prerequisites ✓

- [ ] Backend running on http://localhost:8000
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Frontend running on http://localhost:5173

---

## Step 1: Start Services

### Option A: Manual Start (Recommended)

**Terminal 1 - Backend:**
```powershell
cd C:\Users\hello\Documents\Projects\EasyGrant
uvicorn backend.src.main:app --reload
```
✅ Wait for: `Application startup complete.`

**Terminal 2 - Frontend:**
```powershell
cd C:\Users\hello\Documents\Projects\EasyGrant\frontend
npm install  # First time only
npm run dev
```
✅ Wait for: `Local: http://localhost:5173/`

### Option B: Automated Start

```powershell
cd C:\Users\hello\Documents\Projects\EasyGrant
.\start-dev.ps1
```

---

## Step 2: Open Browser

**Navigate to**: http://localhost:5173

**Expected**:
- ✅ Page loads without errors
- ✅ Header: "🎯 EasyGrant Smart Proposal Assistant"
- ✅ Upload panel with two sections
- ✅ Quota display: "0.0 / 50 MB"
- ✅ No errors in browser console (F12)

---

## Step 3: Test Funding Call Upload

### 3.1 Prepare Test File
- Find any PDF file on your computer (< 10MB)
- Examples: research paper, report, ebook, documentation

### 3.2 Upload via Drag & Drop
1. **Drag** PDF file over "Funding Call" dropzone
   - ✅ Dropzone highlights (green border)
2. **Drop** file
   - ✅ File preview appears (name + size)
3. **Click** "Upload & Index Funding Call"
   - ✅ Progress bar animates (0% → 100%)
   - ✅ Message: "Uploading... 50%" → "Indexing document..."
   - ✅ Success: "✓ Funding call uploaded! X chunks indexed"
   - ✅ Quota updates (e.g., "2.5 / 50 MB")

### 3.3 Upload via File Picker
1. **Click** "browse" link
2. **Select** PDF file from dialog
3. **Click** "Upload & Index Funding Call"
   - ✅ Same behavior as drag & drop

---

## Step 4: Test Supporting Documents Upload

### 4.1 Prepare Test Files
- Find 2-3 PDF or DOCX files (< 10MB each)
- Total size should be < 50MB

### 4.2 Upload Multiple Files
1. **Drag** multiple files over "Supporting Docs" dropzone
   - ✅ All files appear in list
2. **Remove** one file (click × button)
   - ✅ File removed from list
3. **Click** "Upload & Index X Documents"
   - ✅ Progress bar animates
   - ✅ Success: "X documents uploaded! Y total chunks indexed"
   - ✅ Uploaded summary appears with chunk counts

### 4.3 Check File List
- ✅ Each uploaded file shows:
  - Filename
  - Chunk count (e.g., "12 chunks")
  - Green checkmark ✓

---

## Step 5: Test Error Handling

### 5.1 Invalid File Type
1. **Try uploading** .txt, .jpg, or .zip file
   - ✅ Error toast: "Invalid file type..."
   - ✅ Toast auto-dismisses after 5 seconds

### 5.2 Oversized File
1. **Try uploading** PDF > 10MB
   - ✅ Error toast: "File too large. Maximum size: 10MB"

### 5.3 Too Many Files
1. **Try uploading** 6 supporting documents
   - ✅ Error toast: "Maximum 5 supporting documents allowed"

### 5.4 Quota Exceeded
1. **Upload files** until close to 50MB
2. **Try uploading** large file that would exceed quota
   - ✅ Error toast: "Upload would exceed 50MB quota"

---

## Step 6: Verify Backend

### 6.1 Check Backend Logs
**Terminal 1** (backend logs should show):
```
INFO:     POST /api/session/create - 200 OK
INFO:     POST /api/upload/funding-call - 200 OK
INFO:     POST /api/upload/supporting-docs - 200 OK
```

### 6.2 Test API Docs
**Navigate to**: http://localhost:8000/docs

- ✅ Swagger UI loads
- ✅ Try "POST /api/session/create" → Click "Try it out" → Execute
- ✅ Response: `{"session_id": "...", "created_at": "...", "quota": {...}}`

### 6.3 Check File Storage
**Open folder**: `C:\Users\hello\Documents\Projects\EasyGrant\data\uploads\`

- ✅ Session folder exists (e.g., `abc-123-def-456/`)
- ✅ Uploaded files visible with UUID names (e.g., `xyz-789.pdf`)

---

## Step 7: Test Quota Display

### 7.1 Real-time Updates
1. **Upload** 5MB file
   - ✅ Quota shows ~5MB / 50MB
   - ✅ Progress bar fills proportionally (~10%)
2. **Upload** another 10MB file
   - ✅ Quota shows ~15MB / 50MB
   - ✅ Progress bar at ~30%

### 7.2 File Count
1. **Upload** 3 supporting docs
   - ✅ File count shows "3 / 5 files"
2. **Try uploading** 3 more files
   - ✅ Error after 5th file: "Maximum 5 documents"

---

## Step 8: Browser Console Check

**Open DevTools** (F12) → Console tab

### Expected (No Errors):
```
Session created: abc-123-def-456
Upload complete: funding-call {success: true, chunk_count: 23}
```

### Common Issues:
❌ `CORS policy error` → Check backend CORS settings
❌ `404 Not Found` → Check API base URL in `.env`
❌ `Network error` → Backend not running

---

## ✅ Success Checklist

After testing, you should have verified:

- [ ] Page loads without errors
- [ ] Session auto-created on page load
- [ ] Funding call PDF upload works
- [ ] Progress indicator shows upload + indexing
- [ ] Success message displays chunk count
- [ ] Quota updates after upload
- [ ] Supporting docs upload works (multiple files)
- [ ] Uploaded files list appears
- [ ] Error toasts work for invalid files
- [ ] Drag & drop visual feedback works
- [ ] File removal works (× button)
- [ ] Backend logs show successful API calls
- [ ] Files stored in `/data/uploads/{session_id}/`

---

## 🐛 Troubleshooting

### Backend won't start
```powershell
# Check if port 8000 is already in use
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <PID> /F
```

### Frontend won't start
```powershell
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -r node_modules
npm install
```

### CORS errors
**Fix**: Update `backend/src/main.py`:
```python
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
]
```

### Files not uploading
1. Check browser console for errors
2. Check backend logs for API errors
3. Verify OpenAI API key is set (for indexing)
4. Test with smaller files (< 1MB) first

---

## 📖 Next Steps

After successful testing:
1. ✅ Backend + Frontend working locally
2. 🚀 Deploy to Render (see `TESTING_FRONTEND.md`)
3. 📝 Continue with Phase 4 (Requirements Extraction)

---

**Need detailed instructions?** See `TESTING_FRONTEND.md`
